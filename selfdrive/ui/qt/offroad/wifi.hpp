#pragma once

#include <QWidget>
#include <QButtonGroup>
#include <QVBoxLayout>
#include <QStackedWidget>
#include <QTimer>

#include "wifiManager.hpp"
#include "widgets/input_field.hpp"


class WifiUI : public QWidget {
  Q_OBJECT

public:
  int page;
  explicit WifiUI(QWidget *parent = 0, int page_length = 8);

private:
  WifiManager* wifi;
  const int networks_per_page;

  QStackedWidget *swidget;
  QVBoxLayout *vlayout;
  QWidget *wifi_widget;

  InputField *input_field;
  QEventLoop loop;
  QTimer *timer;
  QString text;
  QButtonGroup *connectButtons;

  void connectToNetwork(Network n);
  QString getStringFromUser();

private slots:
  void handleButton(QAbstractButton* m_button);
  void refresh();
  void receiveText(QString text);
  void wrongPassword(QString ssid);

  void prevPage();
  void nextPage();

signals:
  void openKeyboard();
  void closeKeyboard();
};
