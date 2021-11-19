import requests  # for getting URL
import pandas as pd
import datetime as dt
from typing import Match
import re


class whoopUser:
    def __init__(self, email, password):
        self.BASE_URL = "https://api-7.whoop.com/"
        self.AUTH_URL = self.BASE_URL + "oauth/token"
        self.login(email, password)
        self.header = {"Authorization": "bearer {}".format(self.token)}
        self.CYCLES_URL = "users/{}/cycles".format(self.user_id)
        self.HEART_RATE_URL = self.BASE_URL + f"users/{self.user_id}/metrics/heart_rate"

    def login(self, email, password):
        """
        Login to whoop API, storing User id and token
        :param email: str email
        :param password: str password
        :return: None will set class variables
        """
        login = requests.post(
            self.AUTH_URL,
            json={
                "grant_type": "password",
                "issueRefresh": True,
                "password": password,
                "username": email,
            },
        )
        if login.status_code != 200:
            raise AssertionError("Credentials rejected")
        login_data = login.json()
        self.token = login_data["access_token"]
        self.user_id = login_data["user"]["id"]

    default_params = {
        "start": "2000-01-01T00:00:00.000Z",
        "end": "2030-01-01T00:00:00.000Z",
    }

    def get_cycles_json(self, params=default_params):
        """
        Record base information
        :param params: start, end, other params
        :return: json with all info from cycles endpoint
        """
        cycles_URL = "https://api-7.whoop.com/users/{}/cycles".format(self.user_id)
        cycles_request = requests.get(cycles_URL, params=params, headers=self.header)
        return cycles_request.json()

    def get_cycles_df(self, params=default_params):
        """
        :param params: params for cycle query
        :return: dataframe with all the cycle info
        """
        df_columns = [
            "id",
            "day",
            "rMSSD",
            "resting_hr",
            "recovery_score",
            "n_naps",
            "sleep_need_baseline",
            "sleep_debt",
            "sleep_need_strain",
            "sleep_need_total",
            "sleep_quality_duration",
            "avg_hr",
            "kilojoules",
            "max_hr",
            "strain_score",
        ]
        result_df = pd.DataFrame(columns=df_columns)
        json_data = self.get_cycles_json(params=params)
        for day in json_data:
            if not (
                day["recovery"]
                and "timestamp" in day["recovery"]
                and "heartRateVariabilityRmssd" in day["recovery"]
                and isinstance(
                    day["recovery"]["heartRateVariabilityRmssd"], (int, float)
                )
                and day["sleep"]
                and day["sleep"]["sleeps"]
                and day["sleep"]["sleeps"][0]["timezoneOffset"]
            ):
                continue
            day_data = day
            series_dict = {}
            series_dict["id"] = day_data["id"]
            series_dict["day"] = day_data["days"][0]
            series_dict["n_naps"] = len(day_data["sleep"]["naps"])
            recovery_data = day_data["recovery"]
            series_dict["rMSSD"] = recovery_data["heartRateVariabilityRmssd"]
            series_dict["resting_hr"] = recovery_data["restingHeartRate"]
            series_dict["recovery_score"] = recovery_data["score"]
            if day_data["sleep"]["needBreakdown"] is None:
                series_dict["sleep_need_baseline"] = 0
                series_dict["sleep_debt"] = 0
                series_dict["sleep_need_strain"] = 0
                series_dict["sleep_need_total"] = 0
            else:
                need_breakdown = day_data["sleep"]["needBreakdown"]
                series_dict["sleep_need_baseline"] = need_breakdown["baseline"]
                series_dict["sleep_debt"] = need_breakdown["debt"]
                series_dict["sleep_need_strain"] = need_breakdown["strain"]
                series_dict["sleep_need_total"] = need_breakdown["total"]
            series_dict["sleep_quality_duration"] = day_data["sleep"]["qualityDuration"]
            strain_data = day_data["strain"]
            series_dict["avg_hr"] = strain_data["averageHeartRate"]
            series_dict["kilojoules"] = strain_data["kilojoules"]
            series_dict["max_hr"] = strain_data["maxHeartRate"]
            series_dict["strain_score"] = strain_data["score"]
            result_df = result_df.append(series_dict, ignore_index=True)
        return result_df

    def get_sleeps_df(self, params=default_params):
        """
        Will return all sleep data in a dataframe from the cycles endpoint. Done in a seperate method because there is a
        manyToOne type relationship between sleeps and cycles. In most cases there is just one, unless you;ve slept
        multiple times in a day
        :param params: start/end data
        :return: dataframe with sleep data, linked to cycles IDs
        """
        df_cols = [
            "cycle_id",
            "sleep_id",
            "cycles_count",
            "disturbance_count",
            "time_lower_bound",
            "time_upper_bound",
            "in_bed_duration",
            "is_nap",
            "latency_duration",
            "light_sleep_duration",
            "no_data_duration",
            "quality_duration",
            "rem_sleep_duration",
            "respiratory_rate",
            "sleep_score",
            "sleep_consistency",
            "sleep_efficiency",
            "sws_duration",
            "wake_duration",
        ]
        result_df = pd.DataFrame(columns=df_cols)
        cycles_data = self.get_cycles_json(params)
        for day in cycles_data:
            if day["sleep"]["id"] is None:
                continue
            sleep_data = day["sleep"]["sleeps"]
            if len(sleep_data) == 0:
                continue
            cycle_id = day["id"]
            for sleep in sleep_data:
                row_dict = {}
                row_dict["cycle_id"] = cycle_id
                row_dict["sleep_id"] = sleep["id"]
                row_dict["cycles_count"] = sleep["cyclesCount"]
                row_dict["disturbance_count"] = sleep["disturbanceCount"]
                # for some reason whoop leaves all timezone substrings in the
                # datetime string as +0000, and adds a timezone offset field
                # to the response
                tz_as_str = sleep["timezoneOffset"]
                row_dict["time_upper_bound"] = whoopUser.convert_whoop_str_to_datetime(
                    sleep["during"]["upper"], tz_as_str
                )
                row_dict["time_lower_bound"] = whoopUser.convert_whoop_str_to_datetime(
                    sleep["during"]["lower"], tz_as_str
                )
                row_dict["is_nap"] = sleep["isNap"]
                row_dict["in_bed_duration"] = sleep["inBedDuration"]
                row_dict["light_sleep_duration"] = sleep["lightSleepDuration"]
                row_dict["latency_duration"] = sleep["latencyDuration"]
                row_dict["no_data_duration"] = sleep["noDataDuration"]
                row_dict["rem_sleep_duration"] = sleep["remSleepDuration"]
                row_dict["respiratory_rate"] = sleep["respiratoryRate"]
                row_dict["sleep_score"] = sleep["score"]
                row_dict["sleep_efficiency"] = sleep["sleepEfficiency"]
                row_dict["sleep_consistency"] = sleep["sleepConsistency"]
                row_dict["sws_duration"] = sleep["slowWaveSleepDuration"]
                row_dict["wake_duration"] = sleep["wakeDuration"]
                row_dict["quality_duration"] = sleep["qualityDuration"]
                result_df = result_df.append(row_dict, ignore_index=True)
        return result_df

    def get_workouts_df(self, params=default_params):
        """
        Will get all data related to workouts.

        Dataframe will link to cycle IDs
        :param params: start end date
        :return: dataframe
        """
        cycles_data = self.get_cycles_json()
        df_cols = [
            "cycle_id",
            "workout_id",
            "average_hr",
            "cumulative_strain",
            "time_upper_bound",
            "time_lower_bound",
            "kilojoules",
            "strain_score",
            "sport_id",
            "source",
            "time_hr_zone_0",
            "time_hr_zone_1",
            "time_hr_zone_2",
            "time_hr_zone_3",
            "time_hr_zone_4",
            "time_hr_zone_5",
        ]
        result_df = pd.DataFrame(columns=df_cols)
        for day in cycles_data:
            cycle_id = day["id"]
            workout_data = day["strain"]["workouts"]
            if len(workout_data) == 0:
                continue
            for workout in workout_data:
                row_dict = {}
                row_dict["cycle_id"] = cycle_id
                row_dict["workout_id"] = workout["id"]
                row_dict["average_hr"] = workout["averageHeartRate"]
                row_dict["cumulative_strain"] = workout["cumulativeWorkoutStrain"]
                row_dict["time_upper_bound"] = workout["during"]["upper"]
                row_dict["time_lower_bound"] = workout["during"]["lower"]
                row_dict["kilojoules"] = workout["kilojoules"]
                row_dict["strain_score"] = workout["score"]
                row_dict["sport_id"] = workout["sportId"]
                row_dict["source"] = workout["source"]
                zones = workout["zones"]
                for i in range(0, 6):
                    row_dict["time_hr_zone_" + str(i)] = zones[i]
                result_df = result_df.append(row_dict, ignore_index=True)
        return result_df

    default_params_hr = {
        "start": "2020-12-10T00:00:00.000Z",
        "end": "2020-12-16T00:00:00.000Z",
    }

    def get_heart_rate_json(self, params=default_params_hr):
        """
        Get heart rate data on user
        :param params: params for heart rate data
        :return: dict of heart rate data
        """
        hr_request = requests.get(
            self.HEART_RATE_URL, params=params, headers=self.header
        )
        data = hr_request.json()
        return data

    def get_heart_rate_df(self, params=default_params_hr):
        """
        Get heart rate data as a dataframe. Note the maximum range is 8 days.

        Converts thirteen digit UNIX timestamp to
        normal time.
        Can take a very long time to run depending on how many days are specified.
        Maybe optimize later
        :param params: start end range
        :return:dataframe with heart rate data over time
        """
        hr_data = self.get_heart_rate_json(params)
        data = hr_data["values"]
        result_df = pd.DataFrame(columns=["heart_rate", "timestamp"])
        for tick in data:
            row_dict = {}
            row_dict["heart_rate"] = tick["data"]
            row_dict["timestamp"] = whoopUser.convert_unix_time_to_current(tick["time"])
            result_df = result_df.append(row_dict, ignore_index=True)
        return result_df

    def get_sports(self):
        """:return: List of sports and releveant information."""
        sports_url = self.BASE_URL + "sports"
        sports_request = requests.get(sports_url, headers=self.header)
        return sports_request.json()

    def get_sports_df(self):
        """
        Get sports list as a dataframe.
        Converts thirteen digit UNIX timestamp to
        normal time.
        Can take a very long time to run depending on how many days are specified.
        Maybe optimize later
        """
        sports_data = self.get_sports()
        data = sports_data
        result_df = pd.DataFrame(columns=["id", "name", "hasDistanceDetails", "category"])
        for row in data:
            row_dict = {}
            row_dict["id"] = row["id"]
            row_dict["name"] = row["name"]
            row_dict["hasDistanceDetails"] = row["hasGps"]
            row_dict["category"] = row["category"]
            result_df = result_df.append(row_dict, ignore_index=True)
        return result_df

    @staticmethod
    def convert_unix_time_to_current(timestamp):
        """will use local timezone for moment."""
        time = dt.datetime.fromtimestamp(int(timestamp) / 1000)
        return time.strftime("%Y-%m-%d %H:%M:%S")

    @staticmethod
    def convert_whoop_str_to_datetime(whoop_dt: str, tz: str) -> dt.datetime:
        """
        Make proper datetimes out of this.

        sometimes microseconds are given with 2 digits, not 3
        pad with zero if necessary
        """

        def zero_pad_microseconds(mseconds: Match) -> str:
            return f".{mseconds.group(1).ljust(3, '0')}+"

        adjusted_str = re.sub(r"\.([0-9]{0,3})\+", zero_pad_microseconds, whoop_dt)

        def correct_tz(tz_match: Match) -> str:
            return f"{tz[:3]}:{tz[3:]}"

        final_str = re.sub(r"([\+|\-][0-9]{2}:[0-9]{2})", correct_tz, adjusted_str)

        return dt.datetime.fromisoformat(final_str)


