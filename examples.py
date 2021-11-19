from user import whoopUser

email = "stroutcr@gmail.com"
password = "newpass1"
user = whoopUser(email, password)

#get all cycle data
#cycles_data = user.get_cycles_df()

#get all workouts
#workout_data = user.get_workouts_df()

#get heart rate data for one day
start_end ={
        'start': '2021-11-16T05:00:00.000Z',
        'end': '2021-11-17T05:00:00.000Z'
    }
#hr_data = user.get_heart_rate_df(params=start_end)

#get all sleep data
#sleep_data = user.get_sleeps_df()

sport_data = user.get_sports_df()

if __name__ == "__main__":
    #print(str(hr_data))
    print(str(sport_data))