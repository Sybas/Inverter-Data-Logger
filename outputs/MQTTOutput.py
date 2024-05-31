import PluginLoader
from datetime import datetime
import paho.mqtt.client as mqtt # pip install paho-mqtt

class MWTTOutput(PluginLoader.Plugin):
        """Outputs the data from the inverter logger to an MQTT server """

        def process_message(self, msg):
                mqttc = mqtt.Client()
                mqttc.username_pw_set(self.config.get('mqtt', 'user'),
                                      self.config.get('mqtt', 'pass'))

                mqtt_topic = ''.join([self.config.get('mqtt', 'topic'), "/", msg.id, "/"])
                self.logger.debug('mqtt_topic: '+ mqtt_topic)

                mqttc.connect( self.config.get('mqtt', 'host'),
                                int(self.config.get('mqtt', 'port')), 60)

                mqttc.publish(mqtt_topic + "e_total", ((((msg.e_today*10)-(int(msg.e_today*10)))/10)+msg.e_total))
                mqttc.publish(mqtt_topic + "e_today", msg.e_today)
                mqttc.publish(mqtt_topic + "h_total", msg.h_total)
                mqttc.publish(mqtt_topic + "ac_power", msg.p_ac(1))
                # sometimes the inverter gives 514,7 as temperature, don't send temp then!
                if (msg.temp<300 and self.config.getboolean('general', 'use_temperature')):
                    mqttc.publish(mqtt_topic + "temp", msg.temp)
                else: self.logger.error('temperature out of range: '+str(msg.temp))

                for x in [1,2,3]:
                        mqttc.publish(mqtt_topic + "v_pv" + str(x), msg.v_pv(x))
                        mqttc.publish(mqtt_topic + "i_pv" + str(x), msg.i_pv(x))
                        mqttc.publish(mqtt_topic + "v_ac" + str(x), msg.v_ac(x))
                        mqttc.publish(mqtt_topic + "i_ac" + str(x), msg.i_ac(x))
                        mqttc.publish(mqtt_topic + "f_ac" + str(x), msg.f_ac(x))
                        mqttc.publish(mqtt_topic + "p_ac" + str(x), msg.p_ac(x))

                mqttc.loop(2)
                mqttc.disconnect()
