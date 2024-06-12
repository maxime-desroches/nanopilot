#!/usr/bin/env python3
import argparse
import bz2
from collections import defaultdict

import matplotlib.pyplot as plt

from cereal import log
from openpilot.tools.lib.logreader import LogReader
from tqdm import tqdm

MIN_SIZE = 0.5  # Percent size of total to show as separate entry


def make_pie(msgs, typ):
  msgs_by_type = defaultdict(list)
  for m in msgs:
    msgs_by_type[m.which()].append(m.as_builder().to_bytes())

  total = len(bz2.compress(b"".join([m.as_builder().to_bytes() for m in msgs])))
  uncompressed_total = len(b"".join([m.as_builder().to_bytes() for m in msgs]))

  length_by_type = {k: len(b"".join(v)) for k, v in msgs_by_type.items()}
  # calculate compressed size by calculating diff when removed from the segment
  compressed_length_by_type = {}
  compressed_length_by_type2 = {}

  for field in log.ModelDataV2.schema.non_union_fields:
    # if field not in ('laneLines', 'roadEdges'):
    #   continue
    if field.endswith('DEPRECATED'):
      continue
    schema = log.ModelDataV2.schema.fields[field]
    # print(log.ControlsState.schema.fields['desiredCurvature'].proto.slot.type.which())
    try:
      # print(field)
      which_type = schema.proto.slot.type.which()
      print('Trying', field, which_type)
      new_copy_msgs = b""
      for m in msgs:
        new_m = m.as_builder()
        if m.which() == 'modelV2':
          if which_type == 'text':
            setattr(new_m.modelV2, field, '')
          elif which_type == 'data':
            setattr(new_m.modelV2, field, b'')
          elif which_type == 'bool':
            setattr(new_m.modelV2, field, False)
          elif which_type == 'list':
            setattr(new_m.modelV2, field, [])
          elif which_type == 'struct':
            try:
              setattr(new_m.modelV2, field, log.XYZTData())
            except:
              try:
                setattr(new_m.modelV2, field, log.ModelDataV2.MetaData())
              except:
                setattr(new_m.modelV2, field, log.ModelDataV2.Pose())
          else:
            setattr(new_m.modelV2, field, 0)
          # print(getattr(new_m.modelV2, field))
        # print(new_m.to_bytes())
        new_copy_msgs += new_m.to_bytes()
      compressed_length_by_type2[f"modelV2.{field}"] = total - len(bz2.compress(new_copy_msgs))
      print(f"Saved: {compressed_length_by_type2[f'modelV2.{field}'] / 1024:.2f} kB\n")
    except Exception as e:
      pass
      print(e)

  for field in log.LiveLocationKalman.schema.non_union_fields:
    if field.endswith('DEPRECATED'):
      continue
    schema = log.LiveLocationKalman.schema.fields[field]
    # print(log.ControlsState.schema.fields['desiredCurvature'].proto.slot.type.which())
    try:
      # print(field)
      which_type = schema.proto.slot.type.which()
      print('Trying', field, which_type)
      new_copy_msgs = b""
      for m in msgs:
        new_m = m.as_builder()
        if m.which() == 'liveLocationKalman':
          if which_type == 'text':
            setattr(new_m.liveLocationKalman, field, '')
          elif which_type == 'bool':
            setattr(new_m.liveLocationKalman, field, False)
          elif which_type == 'list':
            setattr(new_m.liveLocationKalman, field, [])
          elif which_type == 'struct':
            setattr(new_m.liveLocationKalman, field, log.LiveLocationKalman.Measurement())
          else:
            setattr(new_m.liveLocationKalman, field, 0)
          # print(getattr(new_m.liveLocationKalman, field))
        # print(new_m.to_bytes())
        new_copy_msgs += new_m.to_bytes()
      compressed_length_by_type2[f"liveLocationKalman.{field}"] = total - len(bz2.compress(new_copy_msgs))
      print(f"Saved: {compressed_length_by_type2[f'liveLocationKalman.{field}'] / 1024:.2f} kB\n")
    except Exception as e:
      pass
      print(e)

  # for k in tqdm(msgs_by_type.keys(), desc="Compressing"):
  #   compressed_length_by_type[k] = total - len(bz2.compress(b"".join([m.as_builder().to_bytes() for m in msgs if m.which() != k])))

  # compressed_length_by_type |= compressed_length_by_type2
  compressed_length_by_type = compressed_length_by_type2

  sizes = sorted(compressed_length_by_type.items(), key=lambda kv: kv[1])

  print("name - comp. size (uncomp. size)")
  for (name, sz) in sizes:
    print(f"{name:<45} - {sz / 1024:.2f} kB ({length_by_type.get(name, 0) / 1024:.2f} kB)")
  print()
  print(f"{typ} - Real total {total / 1024:.2f} kB")
  print(f"{typ} - Breakdown total {sum(compressed_length_by_type.values()) / 1024:.2f} kB")
  print(f"{typ} - Uncompressed total {uncompressed_total / 1024 / 1024:.2f} MB")

  sizes_large = [(k, sz) for (k, sz) in sizes if sz >= total * MIN_SIZE / 100]
  sizes_large += [('other', sum(sz for (_, sz) in sizes if sz < total * MIN_SIZE / 100))]

  labels, sizes = zip(*sizes_large, strict=True)
  print(labels)

  def make_label(pct, allvals):
    absolute = int(pct / 100. * sum(allvals))
    return f"{pct:.1f}% ({absolute/1024:.1f} kB)"

  plt.figure()
  plt.title(f"{typ}")
  plt.pie(sizes, labels=labels, autopct=lambda pct: make_label(pct, sizes), pctdistance=0.8)


if __name__ == "__main__":
  parser = argparse.ArgumentParser(description='View log size breakdown by message type')
  parser.add_argument('route', help='route to use')
  args = parser.parse_args()

  msgs = list(LogReader(args.route))

  make_pie(msgs, 'qlog')
  plt.show()
