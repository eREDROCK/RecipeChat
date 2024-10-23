import MeCab
import requests
import json
import requests
from pprint import pprint

applicationId= "xxxx" #自分の楽天APIのApplication IDに置き換えてください

def analyze_input():
    while True:
        input_text = input(">> ")
        mecab = MeCab.Tagger()  # MeCabを使って解析
        parsed = mecab.parse(input_text)
        nouns = []
        
        # 形態素解析結果を行ごとに分解
        for line in parsed.splitlines():
            if line == 'EOS':
                break
            parts = line.split('\t')
            if len(parts) > 3:
                word = parts[0]
                pos = parts[4]
                if '名詞' in pos:
                    nouns.append(word)
        
        if nouns:
            return nouns
        else:
            print("もう一度入力してください。")

def get_category(nouns):
    res = requests.get(f"https://app.rakuten.co.jp/services/api/Recipe/CategoryList/20170426?applicationId={applicationId}")
    json_data = json.loads(res.text)
    # カテゴリデータを格納するリスト
    category_list = []

    # 中カテゴリの親を保存する辞書
    parent_dict = {}

    # 大カテゴリを追加
    for category in json_data['result']['large']:
        category_list.append({
            'category1': category['categoryId'],
            'category2': "",
            'category3': "",
            'categoryId': category['categoryId'],
            'categoryName': category['categoryName']
        })

    # 中カテゴリを追加
    for category in json_data['result']['medium']:
        category_list.append({
            'category1': category['parentCategoryId'],
            'category2': category['categoryId'],
            'category3': "",
            'categoryId': str(category['parentCategoryId']) + "-" + str(category['categoryId']),
            'categoryName': category['categoryName']
        })
        # 中カテゴリの親カテゴリIDを保存
        parent_dict[str(category['categoryId'])] = category['parentCategoryId']

    # 小カテゴリを追加
    for category in json_data['result']['small']:
        category_list.append({
            'category1': parent_dict[category['parentCategoryId']],
            'category2': category['parentCategoryId'],
            'category3': category['categoryId'],
            'categoryId': parent_dict[category['parentCategoryId']] + "-" + str(category['parentCategoryId']) + "-" + str(category['categoryId']),
            'categoryName': category['categoryName']
        })
    
    for noun in nouns:
        # 食材名が含まれるカテゴリを検索
        for category in category_list:
            if noun in category['categoryName']:
                return category['categoryId']
    return None  # 該当するカテゴリが見つからなかった場合

# レシピ検索の関数
def get_recipe_by_ingredient(ingredient):
    categoryId=get_category(ingredient)
    if categoryId is None:
        print("カテゴリの取得に失敗しました")
        return
    url = "https://app.rakuten.co.jp/services/api/Recipe/CategoryRanking/20170426"
    
    params = {
        "applicationId": applicationId,
        "categoryId": categoryId,  
        "format": "json"
    }
    
    # APIリクエストを送信
    response = requests.get(url, params=params)
    
    # レスポンスのステータスコードを確認
    if response.status_code == 200:
        recipes = response.json().get('result', [])
        print("こんなレシピはいかがでしょうか？")
        
        # レシピを表示
        for recipe in recipes:
            title = recipe.get('recipeTitle')
            url = recipe.get('recipeUrl')
            print(f"レシピ名: {title}")
            print(f"URL: {url}")
            print("------")
    else:
        print("レシピの取得に失敗しました")

if __name__ == "__main__":
    print("今日食べたい食材を1つ教えてください")
    nouns=analyze_input()
    get_recipe_by_ingredient(nouns)