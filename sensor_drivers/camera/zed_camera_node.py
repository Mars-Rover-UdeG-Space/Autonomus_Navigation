#!/usr/bin/env python3
    # Author: Samuel Briones Nava
    # Date: 07/09/2024
    # Description: Este nodo publica la información de los sensores IMU, magnetometro y barometro, 
    # además del stream de video.

    # Example Usage:
    # rosrun sensor_drivers zedCamera.launch

import rospy
from sensor_msgs.msg import Imu, MagneticField, FluidPressure
import zed_class

def main():
    # Initialize the ROS node
    rospy.init_node('zed_node', anonymous=True)
    
    # Create publishers for IMU, barometer, and magnetometer data
    imu_pub = rospy.Publisher('imu', Imu, queue_size=10)
    bar_pub = rospy.Publisher('barometer', FluidPressure, queue_size=10)
    magnet_pub = rospy.Publisher('magnetometer', MagneticField, queue_size=10)
    
    # Set the rate of publishing messages (10 Hz)
    rate = rospy.Rate(5)
    
    # Create an instance of the ZED_sensors class
    zed = zed_class.ZED_sensors()
    
    zed.videoStream()
    while not rospy.is_shutdown():
        # Keep streaming 
        err = zed.zed.grab(zed.runtime)
        # if err == sl.ERROR_CODE.SUCCESS: 
        #     sleep(0.001)

        sensors_data = zed.getSensorsData()
        
        # Retrieve sensor data from the ZED camera
        imu_pub.publish(sensors_data[0])
        bar_pub.publish(sensors_data[1])
        magnet_pub.publish(sensors_data[2])
        
        # Log a message indicating that data has been published
        rospy.loginfo("Video, IMU, Barometer, and Magnetometer data have been published")
        
        # Sleep for the remainder of the cycle to maintain the desired rate
        rate.sleep()
    else:
        zed.zed.disable_streaming()
        zed.zed.close()

if __name__ == '__main__':
    try:
        main()
    except rospy.ROSInterruptException:
        # Handle exception if the ROS node is interrupted
        pass
