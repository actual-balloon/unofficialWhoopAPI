import requests  # for getting URL
import pandas as pd
import datetime as dt
from typing import Match
import re

class whoopUserData:
    def __init__(self, email, password):
        self.BASE_URL = "https://api.prod.whoop.com/"
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
        "start": "2022-02-17T00:00:00.000Z",
        "end": "2022-02-18T00:00:00.000Z",
    }

    def get_cycles_json(self, params=default_params):
        """
        Record base information
        :param params: start, end, other params
        :return: json with all info from cycles endpoint
        """
        cycles_URL = "https://api.prod.whoop.com/activities-service/v1/cycles/aggregate/range/{}".format(self.user_id)
        cycles_request = requests.get(cycles_URL, params=params, headers=self.header)
        return cycles_request.json()

    def get_cycles_df(self, params=default_params):
        """
        :param params: params for cycle query
        :return: dataframe with all the cycle info
        """

        df_cycle_columns = {
            "id",
            "created_at",
            "updated_at",
            "scaled_strain",
            "during",
            "user_id",
            "sleep_need",
            "predicted_end",
            "timezone_offset",
            "intensity_score",
            "data_state",
            "day_strain",
            "day_kilojoules",
            "day_avg_heart_rate",
            "day_max_heart_rate"
        }

        df_sleeps_columns = {
            "cycle_id",
            "created_at",
            "updated_at",
            "activity_id",
            "during",
            "score",
            "quality_duration",
            "latency",
            "max_heart_rate",
            "average_heart_rate",
            "debt_pre",
            "debt_post",
            "need_from_strain",
            "sleep_need",
            "habitual_sleep_need",
            "disturbances",
            "time_in_bed",
            "light_sleep_duration",
            "slow_wave_sleep_duration",
            "rem_sleep_duration",
            "cycles_count",
            "wake_duration",
            "arousal_time",
            "no_data_duration",
            "in_sleep_efficiency",
            "credit_from_naps",
            "hr_baseline",
            "respiratory_rate",
            "sleep_consistency",
            "algo_version",
            "projected_score",
            "projected_sleep",
            "optimal_sleep_times",
            "kilojoules",
            "user_id",
            "timezone_offset",
            "percent_recorded",
            "auto_detected",
            "state",
            "responded",
            "team_act_id",
            "source",
            "is_normal",
            "is_significant",
            "is_nap"
        }

        df_recovery_columns = {
            "during",
            "id",
            "date",
            "created_at",
            "updated_at",
            "user_id",
            "sleep_id",
            "survey_response_id",
            "cycle_id",
            "responded",
            "recovery_score",
            "resting_heart_rate",
            "hrv_rmssd",
            "state",
            "prob_covid",
            "hr_baseline",
            "skin_temp_celsius",
            "spo2",
            "algo_version",
            "rhr_component",
            "hrv_component",
            "history_size",
            "from_sws",
            "recovery_rate",
            "is_normal"
        }



