import numpy as np

# Define structured dtype for UserEquipment
user_dtype = np.dtype([
    ('id', 'int32'),
    ('traffic_type', 'U20'),  # up to 20-character unicode string
])

# Define traffic profile as a structured array
traffic_profile = np.array([
    ("eMBB", 100e3, 500e3, 1e9),
    ("video", 100e3, 500e3, 10e6),
    ("virtual reality", 10e6, 500e6, 1e9),
    ("URLLC", 100, 50e3, 100e3),
    ("industrial", 100, 500, 10e3),
    ("self-driving car", 10e3, 50e3, 100e3),
    ("mMTC", 10, 50, 100),
    ("sensor data", 10, 50, 100)
], dtype=[('traffic_type', 'U20'), ('min', 'float64'), ('avg', 'float64'), ('max', 'float64')])

def create_user_demand(users, traffic_profile):
  # Initialize an empty array to hold the demands
  demands = np.zeros(users.shape[0])
  # Loop over each user and generate a demand for their traffic type
  for i, user in enumerate(users):
    profile = traffic_profile[traffic_profile['traffic_type'] == user['traffic_type']]
    demand = np.random.uniform(profile['min'], profile['max'])
    demands[i] = demand
  # Create a structured array to hold the user demands
  user_demand = np.zeros(users.shape, dtype=[('id', 'int32'), ('traffic_type', 'U20'), ('demand', 'float64')])
  user_demand['id'] = users['id']
  user_demand['traffic_type'] = users['traffic_type']
  user_demand['demand'] = demands
  return user_demand

# Create a list of users
num_users = 1000
user_types = np.random.choice(traffic_profile['traffic_type'], num_users)
users = np.zeros(num_users, dtype=user_dtype)
users['id'] = np.arange(num_users)
users['traffic_type'] = user_types

# Create user demand matrix
user_demand = create_user_demand(users, traffic_profile)

print(user_demand)
