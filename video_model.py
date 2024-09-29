# recommender.py
import numpy as np
import pandas as pd
import pickle
from collections import defaultdict
from rectools import Columns
from rectools.dataset import Dataset
import warnings
warnings.filterwarnings("ignore")

from catboost import CatBoostRanker, Pool
from sklearn.preprocessing import MinMaxScaler

class VideoRecommender:
    def __init__(self, model_path, history_path, video_path):
        # Загружаем историю просмотров и модель
        self.history = pd.read_parquet(history_path)
        self.history.rename(columns={'event_timestamp': Columns.Datetime, 'video_id': Columns.Item, 'watchtime': Columns.Weight}, inplace=True)
        self.dataset = Dataset.construct(self.history)
        self.videos = pd.read_parquet(video_path)
        self.need = ['v_total_comments', 'v_year_views', 'v_month_views', 'v_week_views',
       'v_day_views', 'v_likes', 'v_dislikes', 'v_duration',
       'v_cr_click_like_7_days', 'v_cr_click_dislike_7_days',
       'v_cr_click_vtop_7_days', 'v_cr_click_long_view_7_days',
       'v_cr_click_comment_7_days', 'v_cr_click_like_30_days',
       'v_cr_click_dislike_30_days', 'v_cr_click_vtop_30_days',
       'v_cr_click_long_view_30_days', 'v_cr_click_comment_30_days',
       'v_cr_click_like_1_days', 'v_cr_click_dislike_1_days',
       'v_cr_click_vtop_1_days', 'v_cr_click_long_view_1_days',
       'v_cr_click_comment_1_days', 'v_is_hidden', 'v_is_deleted',
       'v_avg_watchtime_1_day', 'v_avg_watchtime_7_day',
       'v_avg_watchtime_30_day', 'v_frac_avg_watchtime_1_day_duration',
       'v_frac_avg_watchtime_7_day_duration',
       'v_frac_avg_watchtime_30_day_duration',
       'v_category_popularity_percent_7_days',
       'v_category_popularity_percent_30_days', 'v_long_views_1_days',
       'v_long_views_7_days', 'v_long_views_30_days', 'category_id']

        with open(model_path, 'rb') as f:
            self.lightfm = pickle.load(f)

        with open('models/video_model/ranker.cbm', 'rb') as f:
            self.ranker = CatBoostRanker().load_model("models/video_model/ranker.cbm")

    def recommend(self, user_id=1, items_liked=None, items_disliked=None, videos_seen=[]):
        # Если есть понравившиеся видео, то ищем похожие.
        if items_liked:
            recos = self.lightfm.recommend_to_items(
                target_items=items_liked,
                dataset=self.dataset,
                k=10 + 10 * len(items_disliked) if items_disliked is not None else 10
            )
        print(recos)
        else:  # выбираем рандомные видео среди предложенных моделью
            recos = self.lightfm.recommend(
                users=[user_id],
                dataset=self.dataset,
                k=100,
                filter_viewed=True
            ).iloc[np.random.randint(500, size=100)]
        print(recos)
        # используем defaultdict для суммирования score по item_id
        recommendations = defaultdict(float)
        print(defaultdict)
        # добавляем рекомендации и суммируем их score
        for item_id, score in zip(recos['item_id'], recos['score']):
            recommendations[item_id] += score

        if items_disliked:
            # получаем плохие рекомендации
            bad_recos = self.lightfm.recommend_to_items(
                target_items=items_disliked,
                dataset=self.dataset,
                k=5
            )

            # преобразуем в множество плохие item_id для фильтрации
            bad_items = set(bad_recos['item_id'])

            # убираем нежелательные рекомендации
            recommendations = {item_id: score for item_id, score in recommendations.items() if item_id not in bad_items}

        # убираем из рекомендаций уже увиденное    
        recommendations = {item_id: score for item_id, score in recommendations.items() if item_id not in set(videos_seen)}

        # сортируем рекомендации по убыванию score
        sorted_recommendations = sorted(recommendations.items(), key=lambda x: x[1], reverse=True)
        
        # Возвращаем топ 100 рекомендаций

        ids = list(pd.DataFrame(sorted_recommendations[:50])[0])

        top100videos = self.videos[self.videos['video_id'].isin(ids)]
        # ранжируем катбустом
        scores = pd.DataFrame(data=MinMaxScaler().fit_transform((self.ranker.predict(top100videos[self.need])).reshape(-1, 1)), columns=['score'])
        
        videos_to_rec = pd.concat([top100videos, scores], axis=1)

        ids = videos_to_rec.sort_values(by='score', ascending=False)['video_id'][:10]

        recc = self.videos[self.videos['video_id'].isin(ids)][['title', 'description', 'v_pub_datetime', 'video_id', 'category_id']]


        
        return recc.to_json(orient='records')
