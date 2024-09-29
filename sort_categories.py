def reorder_categories(categories, reaction, tiktok_categories):
    if reaction == 1:
        liked_categories = [cat for cat in categories if cat[1].lower() in tiktok_categories]
        other_categories = [cat for cat in categories if cat[1].lower() not in tiktok_categories]
        reordered_categories = liked_categories + other_categories
    else:
        reordered_categories = categories

    for index, category in enumerate(reordered_categories):
        category[0] = index + 1

    return reordered_categories
