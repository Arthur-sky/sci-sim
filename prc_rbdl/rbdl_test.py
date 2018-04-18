# --------------------------------------
# 本例模型： 三连杆模型
#               j2 ⊙-------- j3
#      | G        /     b3
#      ↓         / b2
#    j0   b1    /
# Base⊙-------⊙ j1
# ---------------------------------------
import numpy as np
import rbdl
import matplotlib.pyplot as plt
import matplotlib.animation as animation


l1, l2, l3 = [0.5, 0.4, 0.6]
m1, m2, m3 = [1.0, 2.0, 3.0]


model = rbdl.Model()
model.gravity = np.array([0.0, 0.0, -9.81])
# 1. 创建三个body
ixx = m1 * l1 * l1 / 12
izz = ixx
b1 = rbdl.Body.fromMassComInertia(
    m1,
    np.array([0., 0., 0.]),
    np.diag([ixx, 0.0, izz]))
ixx = m2 * l2 * l2 / 12
izz = ixx
b2 = rbdl.Body.fromMassComInertia(
    m2, np.array([0., 0., 0.]),
    np.diag([ixx, 0.0, izz])
)
ixx = m3 * l3 * l3 / 13
izz = ixx
b3 = rbdl.Body.fromMassComInertia(
    m3, np.array([0., 0., 0.]),
    np.diag([ixx, 0.0, izz])
)
# 2. 创建关节，平面浮动平台约束(q1, q2, q3)
planar_float_type = np.array([[1, 0, 0, 0, 0, 0],
                              [0, 0, 0, 0, 1, 0],
                              [0, 0, 0, 0, 0, 1]])
joint_planar_x = rbdl.Joint.fromJointAxes(planar_float_type)
# 创建关节，x轴转动约束(j1, j2)
joint_rot_x = rbdl.Joint.fromJointType("JointTypeRevoluteX")
# 3. 向模型中添加body
trans = rbdl.SpatialTransform()
trans.r = np.array([0.0, 1.0, 1.0])        # floating base位置
b_base = model.AppendBody(trans, joint_planar_x, b1)
trans.r = np.array([0.0, -l2/2, 0.0])      # 关节1相对fb坐标系位置
b_link1 = model.AddBody(b_base, trans, joint_rot_x, b1)
trans.r = np.array([0.0, l2/2, 0.0])       # 关节2相对fb坐标系位置
b_link3 = model.AddBody(b_base, trans, joint_rot_x, b3)

# 添加约束
constrain_set_l1 = rbdl.ConstraintSet()
c_point = np.array([0.0, l1, 0.0])
# 话说这个名字参数居然不是可以不要的，虽然没什么用
constrain_set_l1.AddConstraint(b_link1, c_point, np.array([0., 1., 0.]), 'ground_y'.encode('utf-8'))
constrain_set_l1.AddConstraint(b_link1, c_point, np.array([0., 0., 1.]), 'ground_z'.encode('utf-8'))
constrain_set_l1.Bind(model)

# 基于该模型仿真测试一下
q0 = np.zeros(model.q_size)
qd0 = np.zeros(model.qdot_size)
qdd0 = np.zeros(model.qdot_size)
tau = np.zeros(model.qdot_size)
# 思考：基于约束的仿真出来约束点是否会变化，最佳的仿真效果还是从当前出发
# 不过：我们不用这个来仿真，用来只做当前的控制，是没有问题的
t_cycle = 0.004


# 产生绘图数据
def data_gen(q=q0[:], qd=qd0[:], qdd=qdd0[:]):
    t_max = 3
    for i in range(int(t_max/t_cycle)):
        # 从源文件知道，这个动力学计算是不包括约束的，所以用这个计算约束没用
        rbdl.ForwardDynamics(model, q, qd, tau, qdd)    # 用正运动学计算加速度
        qd = qd + qdd * t_cycle
        q = q + qd * t_cycle
        yield q


def run(data):
    q = data
    j0_p = rbdl.CalcBodyToBaseCoordinates(model, q, b_link1, np.array([0., l1, 0.]))
    j1_p = rbdl.CalcBodyToBaseCoordinates(model, q, b_link1, np.array([0., 0., 0.]))
    j2_p = rbdl.CalcBodyToBaseCoordinates(model, q, b_link3, np.array([0., 0., 0.]))
    j3_p = rbdl.CalcBodyToBaseCoordinates(model, q, b_link3, np.array([0., l3, 0.]))

    ax.plot([j0_p[1], j1_p[1]], [j0_p[2], j1_p[2]], 'r')
    ax.plot([j1_p[1], j2_p[1]], [j1_p[2], j2_p[2]], 'b')
    ax.plot([j2_p[1], j3_p[1]], [j2_p[2], j3_p[2]], 'g')


def init():
    ax.set_ylim(-2, 2)
    ax.set_xlim(-2, 2)


fig, ax = plt.subplots()

ax.grid()

ani = animation.FuncAnimation(fig, run, data_gen, blit=False, interval=10, repeat=False, init_func=init)
plt.show()






