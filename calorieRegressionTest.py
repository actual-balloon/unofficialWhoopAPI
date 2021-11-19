from user import whoopUser

email = "stroutcr@gmail.com"
password = "newpass1"
user = whoopUser(email, password)

#get workout data from the run on the 5th
#get hr data for the run on the 15th

workout_data = user.get_workouts_df()
print(str(workout_data))

#format dates to workable dates and times
workout_data['date_day'] = workout_data.time_lower_bound.str[:10]


#get workout from Nov. 16th

workout_nov15 = workout_data[workout_data['date_day'] == "2021-11-16"]

print(str(workout_nov15))