from user import whoopUser
import matplotlib.pyplot as plt

email = "stroutcr@gmail.com"
password = "newpass1"
user = whoopUser(email, password)

#get workout data from the run on the 5th
#get hr data for the run on the 15th

workout_data = user.get_workouts_df()
#print(str(workout_data))

#format dates to workable dates and times
workout_data['date_day'] = workout_data.time_lower_bound.str[:10]


#get workout from Nov. 16th

workout_nov15 = workout_data[workout_data['date_day'] == "2022-02-17"]


#print(str(workout_nov15))
print(workout_nov15.time_lower_bound)
lowerTimeBound = workout_nov15.time_lower_bound
upperTimeBound = workout_nov15.time_upper_bound


start_end = {
        'start': lowerTimeBound,
        'end': upperTimeBound
    }

hr_data_workout_nov15 = user.get_heart_rate_df(params=start_end)

hr_data_workout_nov15['time'] = hr_data_workout_nov15.timestamp.str[11:]
hr_data_workout_nov15.plot(x="time", y=["heart_rate"])
plt.show()

