    # Author: Samuel Briones Nava
    # Date: 07/09/2024
    # Description: Este documento contiene la clase ZED_sensors, 
    # la cual incluye las funciones para obtención de datos de sensores imu, 
    # barometro y magnetometro, así como el stream de video.

    # Example Usage:
    # import zed_class

import pyzed.sl as sl
import rospy
from sensor_msgs.msg import Imu, MagneticField, FluidPressure
from std_msgs.msg import Header

class ZED_sensors:
    def __init__(self, fps=15):
        # Initialize the ZED camera and set its parameters
        self.zed = sl.Camera()
        self.init_params = sl.InitParameters()
        self.init_params.camera_resolution = sl.RESOLUTION.AUTO  # Automatically HD720
        # self.init_params.camera_resolution = sl.RESOLUTION.HD720
        self.init_params.depth_mode = sl.DEPTH_MODE.NONE
        self.init_params.camera_fps = fps
        self.init_params.sdk_verbose = 1
        self.sensors_data = sl.SensorsData()

        # Attempt to open the camera with the specified parameters
        self.error = self.zed.open(self.init_params)
        if self.error != sl.ERROR_CODE.SUCCESS:
            print("Camera Open : " + repr(self.error) + ". Exit program")
        else:
            print("Camera has been initialized successfully")

    def videoStream(self):
        # self.zed
        self.runtime = sl.RuntimeParameters()
        self.stream_params = sl.StreamingParameters()
        print("Streaming on port ", self.stream_params.port) # Get the port used to stream
        self.stream_params.codec = sl.STREAMING_CODEC.H264
        self.stream_params.bitrate = 4000
        status_streaming = self.zed.enable_streaming(self.stream_params) # Enable streaming
        if status_streaming != sl.ERROR_CODE.SUCCESS:
            print("Streaming initialization error: ", status_streaming)
            self.zed.close()
            exit()
    
        # Get the camera information to print the FPS
        cam_info = self.zed.get_camera_information()
        fps = int(cam_info.camera_configuration.fps)
        print(f"[Sample] Camera FPS: {fps}")
        self.exit_app = False

    def getSensorsData(self):
        # Retrieve the current sensor data if the camera is functioning properly
        if self.zed.get_sensors_data(self.sensors_data, sl.TIME_REFERENCE.CURRENT) == sl.ERROR_CODE.SUCCESS:
            imu_data = self.__getIMUData()
            bar_data = self.__getBarometerData()
            magnet_data = self.__getMagnetometerData()
            return imu_data, bar_data, magnet_data  # Return all sensor data
        else:
            rospy.logwarn("Failed to retrieve sensors data.")
            return None, None, None  # Return None if data retrieval fails

    def __getIMUData(self):
        # Initialize an Imu message to store IMU data
        imuMsg = Imu()
        imuMsg.header = Header()
        imuMsg.header.stamp = rospy.Time.now()  # You can use the current time or any other timestamp
        imuMsg.header.frame_id = "ZED"

        # Retrieve the quaternion orientation data from the IMU
        quaternion = self.sensors_data.get_imu_data().get_pose().get_orientation().get()
        
        # Retrieve linear acceleration and angular velocity data from the IMU
        linear_acceleration = self.sensors_data.get_imu_data().get_linear_acceleration()
        angular_velocity = self.sensors_data.get_imu_data().get_angular_velocity()
        
        # Assign the quaternion values to the IMU message orientation
        props = ['x', 'y', 'z', 'w']
        for i, prop in enumerate(props):
            setattr(imuMsg.orientation, prop, quaternion[i])

        # Assign the angular velocity values to the IMU message
        props = ['x', 'y', 'z']
        for i, prop in enumerate(props):
            setattr(imuMsg.angular_velocity, prop, angular_velocity[i])

        # Assign the linear acceleration values to the IMU message
        for i, prop in enumerate(props):
            setattr(imuMsg.linear_acceleration, prop, linear_acceleration[i])

        return imuMsg  # Return the populated IMU message

    def __getBarometerData(self):
        # Initialize a FluidPressure message to store barometer data
        barometerMsg = FluidPressure()
        barometerMsg.header = Header()
        barometerMsg.header.stamp = rospy.Time.now()  # You can use the current time or any other timestamp
        barometerMsg.header.frame_id = "ZED"
        
        # Retrieve the pressure data from the barometer and assign it to the message in hPa
        barometerMsg.fluid_pressure = self.sensors_data.get_barometer_data().pressure/100
        
        return barometerMsg  # Return the populated FluidPressure message

    def __getMagnetometerData(self):
        # Initialize a MagneticField message to store magnetometer data
        magnetometerMsg = MagneticField()
        
        magnetometerMsg.header = Header()
        magnetometerMsg.header.stamp = rospy.Time.now()  # You can use the current time or any other timestamp
        magnetometerMsg.header.frame_id = "ZED"
        
        # Retrieve the calibrated magnetic field data from the magnetometer in uT
        magnetic_field = self.sensors_data.get_magnetometer_data().get_magnetic_field_calibrated()
        
        # Assign the magnetic field values to the MagneticField message
        props = ['x', 'y', 'z']
        for i, prop in enumerate(props):
            setattr(magnetometerMsg.magnetic_field, prop, magnetic_field[i])

        return magnetometerMsg  # Return the populated MagneticField message
