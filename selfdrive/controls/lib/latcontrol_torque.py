import math
import numpy as np
from collections import deque

from cereal import log
from openpilot.common.numpy_fast import interp
from openpilot.selfdrive.controls.lib.latcontrol import LatControl
from openpilot.selfdrive.controls.lib.pid import PIDController
from openpilot.selfdrive.controls.lib.vehicle_model import ACCELERATION_DUE_TO_GRAVITY
from openpilot.selfdrive.controls.lib.drive_helpers import get_friction

# At higher speeds (25+mph) we can assume:
# Lateral acceleration achieved by a specific car correlates to
# torque applied to the steering rack. It does not correlate to
# wheel slip, or to speed.

# This controller applies torque to achieve desired lateral
# accelerations. To compensate for the low speed effects we
# use a LOW_SPEED_FACTOR in the error. Additionally, there is
# friction in the steering wheel that needs to be overcome to
# move it at all, this is compensated for too.

LOW_SPEED_X = [0, 10, 20, 30]
LOW_SPEED_Y = [15, 13, 10, 5]


class NanoFFModel:
  def __init__(self, temperature=1.0):
    self.w_1 = [[0.3452189564704895, -0.15614677965641022, -0.04062516987323761, -0.5960758328437805, 0.3211185932159424, 0.31732726097106934, -0.04430829733610153, -0.37327295541763306, -0.14118380844593048, 0.12712529301643372, 0.2641555070877075, -0.3451094627380371, -0.005127656273543835, 0.6185108423233032, 0.03725295141339302, 0.3763789236545563], [-0.0708412230014801, 0.3667356073856354, 0.031383827328681946, 0.1740853488445282, -0.04695861041545868, 0.018055908381938934, 0.009072160348296165, -0.23640218377113342, -0.10362917929887772, 0.022628149017691612, -0.224413201212883, 0.20718418061733246, -0.016947750002145767, -0.3872031271457672, -0.15500062704086304, -0.06375953555107117], [-0.0838046595454216, -0.0242826659232378, -0.07765661180019379, 0.028858814388513565, -0.09516210108995438, 0.008368706330657005, 0.1689300835132599, 0.015036891214549541, -0.15121428668498993, 0.1388195902109146, 0.11486363410949707, 0.0651545450091362, 0.13559958338737488, 0.04300367832183838, -0.13856294751167297, -0.058136988431215286], [-0.006249868310987949, 0.08809533715248108, -0.040690965950489044, 0.02359287068247795, -0.00766348373144865, 0.24816390872001648, -0.17360293865203857, -0.03676899895071983, -0.17564819753170013, 0.18998438119888306, -0.050583917647600174, -0.006488069426268339, 0.10649101436138153, -0.024557121098041534, -0.103276826441288, 0.18448011577129364]]  # noqa: E501
    self.b_1 = [0.2935388386249542, 0.10967712104320526, -0.014007942751049995, 0.211833655834198, 0.33605605363845825, 0.37722209095954895, -0.16615016758441925, 0.3134673535823822, 0.06695777177810669, 0.3425212800502777, 0.3769673705101013, 0.23186539113521576, 0.5770409107208252, -0.05929069593548775, 0.01839117519557476, 0.03828774020075798]  # noqa: E501
    self.w_2 = [[-0.06261160969734192, 0.010185074992477894, -0.06083013117313385, -0.04531499370932579, -0.08979734033346176, 0.3432150185108185, -0.019801849499344826, 0.3010321259498596], [0.19698476791381836, -0.009238275699317455, 0.08842222392559052, -0.09516377002000809, -0.05022778362035751, 0.13626104593276978, -0.052890390157699585, 0.15569131076335907], [0.0724768117070198, -0.09018408507108688, 0.06850195676088333, -0.025572121143341064, 0.0680626779794693, -0.07648195326328278, 0.07993496209383011, -0.059752143919467926], [1.267876386642456, -0.05755887180566788, -0.08429178595542908, 0.021366603672504425, -0.0006479775765910745, -1.4292563199996948, -0.08077696710824966, -1.414825439453125], [0.04535430669784546, 0.06555880606174469, -0.027145234867930412, -0.07661093026399612, -0.05702832341194153, 0.23650476336479187, 0.0024587824009358883, 0.20126521587371826], [0.006042032968252897, 0.042880818247795105, 0.002187949838116765, -0.017126334831118584, -0.08352015167474747, 0.19801731407642365, -0.029196614399552345, 0.23713473975658417], [-0.01644900068640709, -0.04358499124646187, 0.014584392309188843, 0.07155826687812805, -0.09354910999536514, -0.033351872116327286, 0.07138452678918839, -0.04755295440554619], [-1.1012420654296875, -0.03534531593322754, 0.02167935110628605, -0.01116552110761404, -0.08436500281095505, 1.1038788557052612, 0.027903547510504723, 1.0676132440567017], [0.03843916580080986, -0.0952216386795044, 0.039226632565259933, 0.002778085647150874, -0.020275786519050598, -0.07848760485649109, 0.04803166165947914, 0.015538203530013561], [0.018385495990514755, -0.025189843028783798, 0.0036680365446954966, -0.02105865254998207, 0.04808586835861206, 0.1575016975402832, 0.02703506126999855, 0.23039312660694122], [-0.0033881019335240126, -0.10210853815078735, -0.04877309128642082, 0.006989633198827505, 0.046798162162303925, 0.38676899671554565, -0.032304272055625916, 0.2345031052827835], [0.22092825174331665, -0.09642873704433441, 0.04499409720301628, 0.05108088254928589, -0.10191166400909424, 0.12818090617656708, -0.021021494641900063, 0.09440375864505768], [0.1212429478764534, -0.028194155544042587, -0.0981956496834755, 0.08226924389600754, 0.055346839129924774, 0.27067816257476807, -0.09064067900180817, 0.12580905854701996], [-1.6740131378173828, -0.02066155895590782, -0.05924689769744873, 0.06347910314798355, -0.07821853458881378, 1.2807466983795166, 0.04589352011680603, 1.310766577720642], [-0.09893272817134857, -0.04093599319458008, -0.02502273954451084, 0.09490344673395157, -0.0211324505507946, -0.09021010994911194, 0.07936318963766098, -0.03593116253614426], [-0.08490308374166489, -0.015558987855911255, -0.048692114651203156, -0.007421435788273811, -0.040531404316425323, 0.25889304280281067, 0.06012800335884094, 0.27946868538856506]]  # noqa: E501
    self.b_2 = [0.07973937690258026, -0.010446485131978989, -0.003066520905122161, -0.031895797699689865, 0.006032303906977177, 0.24106740951538086, -0.008969511836767197, 0.2872662842273712]  # noqa: E501
    self.w_3 = [[-1.364486813545227, -0.11682678014039993, 0.01764785870909691, 0.03926877677440643], [-0.05695437639951706, 0.05472218990325928, 0.1266128271818161, 0.09950875490903854], [0.11415273696184158, -0.10069356113672256, 0.0864749327301979, -0.043946366757154465], [-0.10138195008039474, -0.040128443390131, -0.08937158435583115, -0.0048376512713730335], [-0.0028251828625798225, -0.04743027314543724, 0.06340016424655914, 0.07277824729681015], [0.49482327699661255, -0.06410001963376999, -0.0999293103814125, -0.14250673353672028], [0.042802367359399796, 0.0015462725423276424, -0.05991362780332565, 0.1022040992975235], [0.3523194193840027, 0.07343732565641403, 0.04157765582203865, -0.12358107417821884]]  # noqa: E501
    self.b_3 = [0.2653026282787323, -0.058485131710767746, -0.0744510293006897, 0.012550175189971924]
    self.w_4 = [[0.5988775491714478, 0.09668736904859543], [-0.04360569268465042, 0.06491032242774963], [-0.11868984252214432, -0.09601487964391708], [-0.06554870307445526, -0.14189276099205017]]  # noqa: E501
    self.b_4 = [-0.08148707449436188, -2.8251802921295166]

    self.input_norm_mat = np.array([[-3.0, 3.0], [-3.0, 3.0], [0.0, 40.0], [-3.0, 3.0]])
    self.output_norm_mat = np.array([-1.0, 1.0])
    self.temperature = temperature

  def sigmoid(self, x):
    return 1 / (1 + np.exp(-x))

  def relu(self, x):
    return np.maximum(0.0, x)

  def forward(self, x):
    assert x.ndim == 1
    x = (x - self.input_norm_mat[:, 0]) / (self.input_norm_mat[:, 1] - self.input_norm_mat[:, 0])
    x = self.relu(np.dot(x, self.w_1) + self.b_1)
    x = self.relu(np.dot(x, self.w_2) + self.b_2)
    x = self.relu(np.dot(x, self.w_3) + self.b_3)
    x = np.dot(x, self.w_4) + self.b_4
    return x

  def predict(self, x):
    x = self.forward(np.array(x))
    pred = np.random.laplace(x[0], np.exp(x[1]) / self.temperature)
    pred = pred * (self.output_norm_mat[1] - self.output_norm_mat[0]) + self.output_norm_mat[0]
    return float(pred)


class LatControlTorque(LatControl):
  def __init__(self, CP, CI):
    super().__init__(CP, CI)
    self.torque_params = CP.lateralTuning.torque
    self.pid = PIDController(self.torque_params.kp, self.torque_params.ki,
                             k_f=self.torque_params.kf, pos_limit=self.steer_max, neg_limit=-self.steer_max)
    self.torque_from_lateral_accel = CI.torque_from_lateral_accel()
    self.use_steering_angle = self.torque_params.useSteeringAngle
    self.steering_angle_deadzone_deg = self.torque_params.steeringAngleDeadzoneDeg
    self.ff_model = NanoFFModel(temperature=100.0)
    self.history = {key: deque([0, 0, 0], maxlen=3) for key in ["lataccel", "roll_compensation", "vego", "aego"]}
    self.history_counter = 0

  def update_live_torque_params(self, latAccelFactor, latAccelOffset, friction):
    self.torque_params.latAccelFactor = latAccelFactor
    self.torque_params.latAccelOffset = latAccelOffset
    self.torque_params.friction = friction

  def update(self, active, CS, VM, params, steer_limited, desired_curvature, llk):
    pid_log = log.ControlsState.LateralTorqueState.new_message()
    actual_curvature_vm = -VM.calc_curvature(math.radians(CS.steeringAngleDeg - params.angleOffsetDeg), CS.vEgo, params.roll)
    roll_compensation = math.sin(params.roll) * ACCELERATION_DUE_TO_GRAVITY

    if not active:
      output_torque = 0.0
      pid_log.active = False
    else:
      if self.use_steering_angle:
        actual_curvature = actual_curvature_vm
        # curvature_deadzone = abs(VM.calc_curvature(math.radians(self.steering_angle_deadzone_deg), CS.vEgo, 0.0))
      else:
        actual_curvature_llk = llk.angularVelocityCalibrated.value[2] / CS.vEgo
        actual_curvature = interp(CS.vEgo, [2.0, 5.0], [actual_curvature_vm, actual_curvature_llk])
        # curvature_deadzone = 0.0
      desired_lateral_accel = desired_curvature * CS.vEgo ** 2

      # desired rate is the desired rate of change in the setpoint, not the absolute desired curvature
      # desired_lateral_jerk = desired_curvature_rate * CS.vEgo ** 2
      actual_lateral_accel = actual_curvature * CS.vEgo ** 2

      low_speed_factor = interp(CS.vEgo, LOW_SPEED_X, LOW_SPEED_Y)**2
      setpoint = desired_lateral_accel + low_speed_factor * desired_curvature
      measurement = actual_lateral_accel + low_speed_factor * actual_curvature

      # lateral_accel_deadzone = curvature_deadzone * CS.vEgo ** 2
      # gravity_adjusted_lateral_accel = desired_lateral_accel - roll_compensation
      # torque_from_setpoint = self.torque_from_lateral_accel(setpoint, self.torque_params, setpoint,
      #                                                lateral_accel_deadzone, friction_compensation=False)
      # torque_from_measurement = self.torque_from_lateral_accel(measurement, self.torque_params, measurement,
      #                                                lateral_accel_deadzone, friction_compensation=False)
      # pid_log.error = torque_from_setpoint - torque_from_measurement
      # ff = self.torque_from_lateral_accel(gravity_adjusted_lateral_accel, self.torque_params,
      #                                     desired_lateral_accel - actual_lateral_accel,
      #                                     lateral_accel_deadzone, friction_compensation=True)

      state_vector = [roll_compensation, CS.vEgo, CS.aEgo]
      # history_state_vector = list(self.history["lataccel"]) + list(self.history["roll_compensation"]) + list(self.history["vego"]) + list(self.history["aego"])  # noqa: E501
      # torque_from_setpoint = self.ff_model.predict([setpoint] + state_vector + history_state_vector)
      # torque_from_measurement = self.ff_model.predict([measurement] + state_vector + history_state_vector)

      torque_from_setpoint = self.ff_model.predict([setpoint] + state_vector)
      torque_from_measurement = self.ff_model.predict([measurement] + state_vector)

      pid_log.error = torque_from_setpoint - torque_from_measurement
      # ff = self.ff_model.predict([desired_lateral_accel] + state_vector + history_state_vector)
      ff = self.ff_model.predict([desired_lateral_accel] + state_vector)

      friction = get_friction(pid_log.error, 0.0, 0.3, self.torque_params, True)
      ff += friction

      freeze_integrator = steer_limited or CS.steeringPressed or CS.vEgo < 5
      output_torque = self.pid.update(pid_log.error,
                                      feedforward=ff,
                                      speed=CS.vEgo,
                                      freeze_integrator=freeze_integrator)

      pid_log.active = True
      pid_log.p = self.pid.p
      pid_log.i = self.pid.i
      pid_log.d = self.pid.d
      pid_log.f = self.pid.f
      pid_log.output = -output_torque
      pid_log.actualLateralAccel = actual_lateral_accel
      pid_log.desiredLateralAccel = desired_lateral_accel
      pid_log.saturated = self._check_saturation(self.steer_max - abs(output_torque) < 1e-3, CS, steer_limited)

    if self.history_counter % 10 == 0:
      self.history["lataccel"].append(actual_curvature_vm * CS.vEgo ** 2)
      self.history["roll_compensation"].append(roll_compensation)
      self.history["vego"].append(CS.vEgo)
      self.history["aego"].append(CS.aEgo)

    self.history_counter = (self.history_counter + 1) % 10

    # TODO left is positive in this convention
    return -output_torque, 0.0, pid_log
