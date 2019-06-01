import numpy as np
# aliasing necessary for using quaternion name inside as local variable
from quaternion import quaternion as Quaternion
from quaternion import from_rotation_vector

from src.integrate import simps_integrate_delta


def rotate_accelerations(times, accelerations, angular_velocities, headings=None,
                         initial_angular_position=np.array([0, 0, 0])):
    """
    Integrate angular velocities and rotate acceleration vector accordingly.
    Moves from local frame of reference to laboratory one.

    :param times: 1xn numpy array of timestamp
    :param accelerations: 3xn numpy array of accelerations
    :param angular_velocities: 3xn numpy array of angular velocities in rad/s
    :param headings: 1xn angular potion around z from gnss data
    :param initial_angular_position: 1x3 numpy array containing initial angular position vector
    :return: 2 numpy array: 3xn acceleration vector and 4xn angular position as quaternion
    """

    # TODO correct with heading
    # integrate angular_velocities to get a delta theta vector
    delta_thetas = simps_integrate_delta(times, angular_velocities)
    initial_quaternion = np.exp(Quaternion(*initial_angular_position) / 2)
    # create quaternion representing angular position (angular position = rotation_versor * rotation_angle)
    quaternions = from_rotation_vector(delta_thetas[:, 1:].T)
    # cant use np.cumprod because in quaternion to rotate first by q1 then by q2
    # the aggregated quaternion is q2q1 not q1q2
    # so use reduce
    from functools import reduce
    quaternions = np.array(reduce(lambda array, element: [*array, element * array[-1]], quaternions, [initial_quaternion]))
    accelerations = np.array(list(map(lambda x: (x[1] * Quaternion(*x[0]) * ~x[1]).components[1:], zip(accelerations.T, quaternions))))
    angular_positions = np.array([quaternion.components for quaternion in quaternions])
    return accelerations.T, angular_positions.T


def align_to_world(gnss_position, vectors, motion_time):
    """
    Align accelerations to world system (x axis going to east, y to north)

    :param gnss_position: 3xn numpy array. positions from gnss data
    :param vectors: 3xn numpy array
    :param stationary_times: list of tuples
    :param angular_positions:
    :return: 2 numpy array: 3xn numpy array of rotated accelerations and 4xn angular positions as quaternions
    """

    from numpy import sin, cos, arctan2
    # get angle of rotation
    angle_gnss = np.arctan2(gnss_position[1, motion_time], gnss_position[0, motion_time])
    # TODO pay attention using acceleration
    angle_vector = arctan2(vectors[1, motion_time], vectors[0, motion_time])
    # rotation_angle = angle_gnss - angle_vector
    rotation_angle = angle_gnss
    message = "Rotation vector to {} degrees to align to world".format(np.rad2deg(rotation_angle))
    print(message)
    new_vectors = vectors.copy()
    # rotate vector in xy plane
    new_vectors[0] = cos(rotation_angle) * vectors[0] - sin(rotation_angle) * vectors[1]
    new_vectors[1] = sin(rotation_angle) * vectors[0] + cos(rotation_angle) * vectors[1]
    return new_vectors
