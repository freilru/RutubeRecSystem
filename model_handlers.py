import ast
import json

from flask import Flask, request, jsonify

from app.repositories.search_query_model import SearchQueryRepository
from app.repositories.sort_categories import reorder_categories
from app.repositories.video_model import VideoRecommender

app = Flask(__name__)

classes = ['Развлечения', 'Хобби', 'Животные', 'Разное', 'Телепередачи', 'Спорт', 'Недвижимость', 'Сериалы', 'Детям', 'Музыка', 'Юмор', 'Лайфстайл', 'Авто-мото', 'Сад и огород', 'Фильмы', 'Мультфильмы', 'Путешествия', 'Технологии и интернет', 'Лайфхаки', 'Видеоигры', 'Культура', 'Обзоры и распаковки товаров', 'Обучение', 'Здоровье', 'Охота и рыбалка', 'Строительство и ремонт', 'Аниме', 'Эзотерика', 'Еда', 'Интервью', 'Бизнес и предпринимательство', 'Техника и оборудование', 'Психология', 'Наука', 'Красота', 'Природа', 'Дизайн', 'Аудиокниги', 'Аудио']
category_preferences = {i: 0.5 for i in range(1, len(classes) + 1)}

model_search_query = SearchQueryRepository(
    model_path="models/search_query_model/model.safetensors",
    tokenizer_name='DeepPavlov/rubert-base-cased',
    classes=classes)

recommender = VideoRecommender(
    model_path='models/video_model/savefile.pickle', history_path='models/video_model/logs_df_2024-08-06.parquet',   video_path='models/video_model/video_stat.parquet'
)

@app.route('/recommend_video', methods=['POST'])
def recommend():
    data = request.json

    user_id = data.get('user_id', 1)
    items_liked = data.get('items_liked', [])
    items_disliked = data.get('items_disliked', [])
    videos_seen = data.get('videos_seen', [])

    recommended_videos = recommender.recommend(user_id, items_liked, items_disliked, videos_seen)

    return jsonify(recommended_videos)


@app.route('/search_query', methods=['POST'])
def predict():
    data = request.json
    query = data.get('query')

    if not query:
        return jsonify({'error': 'No query provided'}), 400

    predicted_category = model_search_query.predict(query)

    return jsonify({'category': predicted_category})


@app.route('/reorder_categories', methods=['POST'])
def reorder_categories_handler():
    data = request.json

    categories = data.get('categories')
    reaction = data.get('reaction')
    tiktok_categories_marshed = data.get('tiktok_categories')
    tiktok_categories = ast.literal_eval(tiktok_categories_marshed)

    if not categories or reaction is None or not tiktok_categories:
        return jsonify({"error": "Invalid input"}), 400

    reordered_categories = reorder_categories(categories, reaction, tiktok_categories)

    return jsonify({"reordered_categories": reordered_categories})

