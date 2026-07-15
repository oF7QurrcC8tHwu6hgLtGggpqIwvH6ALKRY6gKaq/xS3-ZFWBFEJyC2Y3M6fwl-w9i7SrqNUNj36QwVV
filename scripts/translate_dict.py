# -*- coding: utf-8 -*-
"""
商品名・ジャンルの日本語変換辞書
=====================================
注意: これはLootBar公式の翻訳ではなく、独自の意訳です。
      武器の型番(M4A1, AK47, QBZ-95 等)はそのまま残し、
      スキン名・エディション名の部分のみ日本語化します。
      辞書に無い語彙は英語のまま残り、備考に「未対応語彙あり」と記録されます。
      正確性確認のため、常に元の英語名を別列で保持してください。
"""

import re

# 武器コードの表記ゆれ統一（そのまま残すが、統一だけ行う）
WEAPON_NORMALIZE = {
    "Type 81": "81式",
}

# エディション/ティア語彙（長い語句を先にマッチさせる必要があるので順序が重要）
EDITION_MAP_ORDERED = [
    ("Deluxe Flagship Edition+", "デラックスフラッグシップ版+"),
    ("Deluxe Flagship Edition", "デラックスフラッグシップ版"),
    ("Flagship Edition+", "フラッグシップ版+"),
    ("Flagship Edition", "フラッグシップ版"),
    ("Vanguard Edition", "先鋒版"),
    ("Enjoyment Edition", "お試し版"),
    ("Enjoy Edition", "お試し版"),
    ("Enjoy Version", "お試し版"),
    ("Advancement Edition", "上級版"),
    ("Advanced Edition", "上級版"),
    ("Advance Edition", "上級版"),
    ("Deluxe Edition", "デラックス版"),
    ("Pioneer Edition", "パイオニア版"),
    ("Premium Edition", "プレミアム版"),
    ("Enterprising Edition", "進取版"),
    ("Progressive Edition", "プログレッシブ版"),
    ("Initiative Edition", "イニシアチブ版"),
    ("Aggressive Edition", "アグレッシブ版"),
    ("Anniversary Platinum", "記念プラチナ"),
    ("Anniversary Ultimate", "記念アルティメット"),
    ("Ultimate Divine Weapon", "至高の神器"),
    ("Ultimate Battleship", "至高の戦艦"),
    ("Ultra Supreme", "至高版"),
    ("Awakening", "覚醒"),
]

# 商品テーマ/スキン名（キャラクター名は公式表記を使用。長い語句を先に）
FAMILY_MAP_ORDERED = [
    ("Golden Grandeur", "黄金の威光"),
    ("Mai Shiranui", "不知火舞"),
    ("Second to None", "比類なき者"),
    ("Strongest Human", "最強の人類"),
    ("Power Reverence", "力への畏敬"),
    ("Liberty Wind", "自由の風"),
    ("Dragon Force", "ドラゴンフォース"),
    ("Blaze Firefighters", "業火の消防士"),
    ("Harley Quinn", "ハーレイ・クイン"),
    ("Unit-01", "初号機"),
    ("Unit-02", "弐号機"),
    ("Unit-00", "零号機"),
    ("Pirate Empress", "海賊女帝"),
    ("Tony Tony Chopper", "トニートニー・チョッパー"),
    ("Chopper", "チョッパー"),
    ("乔巴", "チョッパー"),
    ("Zoro", "ゾロ"),
    ("Sanji", "サンジ"),
    ("Luffy", "ルフィ"),
    ("Nyxia", "ニクシア"),
    ("Gaius", "ガイウス"),
    ("Cloud", "クラウド"),
    ("Celestial Sunpiercer", "天穿つ光輝"),
    ("Asakura Hao", "麻倉ハオ"),
    ("Yoh Asakura", "麻倉葉"),
    ("Gunfire Coronation", "銃火の戴冠"),
    ("Dragon War", "龍の戦い"),
    ("Golden Blade", "黄金の刃"),
    ("Spotlight Lead Singer", "スポットライトのボーカル"),
    ("Spotlight Vocalist", "スポットライトのボーカル"),
    ("Light and Night Samsara", "光と夜の輪廻"),
    ("Blue Rose Sword Gun", "青薔薇のソードガン"),
    ("Lambent Light", "揺らめく光"),
    ("Thunder Gun", "サンダーガン"),
    ("Battle of Faith", "信念の戦い"),
    ("Epochal Energy", "新時代のエネルギー"),
    ("Dragon Roar Sky", "龍咆の空"),
    ("Wano Country Infiltration", "ワノ国潜入"),
    ("Model X Commemoration", "モデルX記念"),
    ("Winter Encounter", "冬の出会い"),
    ("Sadaharu", "定春"),
    ("Celestial Traveler", "天界の旅人"),
    ("Dawn Breaker of the Galaxy", "銀河の暁"),
]

# タグ(限定/取引可能)
TAG_MAP_ORDERED = [
    ("(Exclusive)", "（限定）"),
    ("(exclusive)", "（限定）"),
    ("(Tradeable)", "（取引可能）"),
    ("(tradable)", "（取引可能）"),
    ("(Tradable)", "（取引可能）"),
]

# パターンに当てはまらない特殊な商品名（完全一致で変換）
SPECIAL_MAP = {
    "Starway: Mechanical Storm Box": "スターウェイ：機械の嵐 ボックス",
    "Starway: Knife of the Golden Hall Box": "スターウェイ：黄金の間のナイフ ボックス",
    "[Mysterious Garden] Collection Box": "【神秘の庭園】コレクションボックス",
    "Time Garden Day Box": "時の庭園：昼の箱",
    "Time Garden Midnight Box": "時の庭園：真夜中の箱",
    "Hunter × Hunter collaboration Event Tradeable Lucky Draw": "HUNTER×HUNTERコラボイベント 取引可能抽選",
    "Tradable Lucky Draw: Fate/Stay Night [Heaven's Feel]": "取引可能抽選：Fate/stay night [Heaven's Feel]",
    "Tradable collaboration Lucky Draw: Chainsaw Man Phase 2": "取引可能コラボ抽選：チェンソーマン 第2弾",
    "Tradable Lucky Draw: That Time I Got Reincarnated as a Slime Phase 1": "取引可能抽選：転生したらスライムだった件 第1弾",
    "Tradable Lucky Draw: NIJISANJI": "取引可能抽選：にじさんじ",
    "Tradable Lucky Draw: Jujutsu Kaisen Phase 1": "取引可能抽選：呪術廻戦 第1弾",
    "Tradable Lucky Draw: DEATH NOTE": "取引可能抽選：DEATH NOTE",
    "Tradable Lucky Draw: BLEACH Vol.1": "取引可能抽選：BLEACH 第1弾",
    "Tradable Lucky Draw: BLEACH Vol.2": "取引可能抽選：BLEACH 第2弾",
    "Tradeable Lucky Draw: EVA No.3 Limited Edition": "取引可能抽選：エヴァンゲリオン3号機 限定版",
    "Lucky Draw: Attack on Titan collaboration Vol.4 (Tradable)": "抽選：進撃の巨人コラボ 第4弾（取引可能）",
    "Tradable Gacha: Tanjiro Kamado & Mugen Train Supply Box": "取引可能ガチャ：竈門炭治郎＆無限列車 補給ボックス",
    "Tradable Gacha: Tokyo Ghoul Season 6": "取引可能ガチャ：東京喰種 シーズン6",
    "Tradable Gacha: NIJISANJI Vol.4": "取引可能ガチャ：にじさんじ 第4弾",
    "Rainbow Sounds: Planet Speech Box": "虹の音色：惑星のスピーチボックス",
    "Rainbow Sounds: Fantasy Dance Box": "虹の音色：ファンタジーダンスボックス",
    "Frog Surprise - Super rare (Tradeable)": "カエルサプライズ - 超激レア（取引可能）",
    "Shining Dream (Exclusive)": "輝く夢（限定）",
    "Bonnie Cotton Candy (Exclusive)": "ボニー・コットンキャンディ（限定）",
    "Breakout: Golden Treasure (Tradeable)": "ブレイクアウト：黄金の秘宝（取引可能）",
    "Breakout S2: Radiant Golden Treasure (Tradeable)": "ブレイクアウトS2：輝く黄金の秘宝（取引可能）",
    "Breakout S3: Radiant Golden Treasure (Tradeable)": "ブレイクアウトS3：輝く黄金の秘宝（取引可能）",
    "Breakout: Radiant Golden Treasure (Tradeable)": "ブレイクアウト：輝く黄金の秘宝（取引可能）",
    "Panorama: The Sixth Heaven Dark Lord Vehicle Chest (tradable)": "パノラマ：第六天魔王 ビークルチェスト（取引可能）",
    "Palace Crystal Treasure Box (Tradable)": "宮殿クリスタル秘宝箱（取引可能）",
    "\"Azure Sky\" Tradable Gift Box": "「紺碧の空」取引可能ギフトボックス",
    "\"Iridescent Dream\" Tradeable Gift Box": "「虹色の夢」取引可能ギフトボックス",
    "Epochal Energy - Gilt Gift Box": "新時代のエネルギー - 金箔ギフトボックス",
    "Epochal Shadow - Gilt Gift Box": "新時代の影 - 金箔ギフトボックス",
    "New Year Limited Frog Head Surprise - Super Rare (Tradeable)": "新年限定カエル頭サプライズ - 超激レア（取引可能）",
    "S38 Surprise - Super Rare (Tradeable)": "S38サプライズ - 超激レア（取引可能）",
    "S39 Surprise - Super Rare (Tradeable)": "S39サプライズ - 超激レア（取引可能）",
    "S40 Surprise - Super Rare (Tradeable)": "S40サプライズ - 超激レア（取引可能）",
    "Golden Shark Surprise - Super Rare (Tradeable)": "黄金シャークサプライズ - 超激レア（取引可能）",
    "\"Chaos Butterfly\" Tradeable Gift Box": "「混沌の蝶」取引可能ギフトボックス",
    "\"Innocent Fantasy\" Tradeable Gift Box": "「無垢な幻想」取引可能ギフトボックス",
    "\"Agent Nyxia·JK\" Tradeable Gift Box": "「エージェント・ニクシアJK」取引可能ギフトボックス",
    "\"Baking Game\" Tradeable Gift Box": "「ベイキングゲーム」取引可能ギフトボックス",
    "\"Sparkling Promise\" Tradeable Gift Box": "「輝く約束」取引可能ギフトボックス",
    "\"Bounce Phantom\" Tradeable Gift Box": "「バウンスファントム」取引可能ギフトボックス",
    "\"Railway Intern\" Tradeable Gift Box": "「鉄道インターン」取引可能ギフトボックス",
    "\"Broken Sweetie\" Tradeable Gift Box": "「割れたスウィーティー」取引可能ギフトボックス",
    "\"Strawberry Ice Cream\" Tradeable Gift Box": "「ストロベリーアイスクリーム」取引可能ギフトボックス",
    "\"Heart of Wine Romance\" Tradeable Gift Box": "「ワインロマンスの心」取引可能ギフトボックス",
    "\"Cherry Blossom Day\" Tradeable Gift Box": "「桜の日」取引可能ギフトボックス",
    "\"Scarlet Law\" Tradeable Gift Box": "「緋色の掟」取引可能ギフトボックス",
    "\"Modern Times\" Tradeable Gift Box": "「モダンタイムズ」取引可能ギフトボックス",
    "\"Butterfly Tale\" Tradeable Gift Box": "「蝶の物語」取引可能ギフトボックス",
    "【Hug Bear】Tradable Gift Box": "【ハグベア】取引可能ギフトボックス",
    "【白日恋语】可交易礼盒": "【白日恋語】取引可能ギフトボックス",
    "Alloy Wheels": "合金ホイール",
    "Blood Frenzy": "ブラッドフレンジー",
    "Lv. 1 Armor": "Lv.1 アーマー",
    "Explosion Delay": "爆発遅延",
    "Agile Steering": "俊敏ステアリング",
    "Steering Sync": "ステアリング同調",
    "Ultimate Shock Absorption": "究極の衝撃吸収",
    "Inertia Optimization": "慣性最適化",
    "Turbo Speed": "ターボスピード",
    "Power Core": "パワーコア",
    "Best Torque": "最大トルク",
    "Move like the wind.": "風のように駆ける。",
    "Safety First": "安全第一",
    "Get Busy Hands": "手を動かせ",
    "Unicycle Drive": "一輪駆動",
    "Calm and Collected": "冷静沈着",
    "Circuit Control": "サーキットコントロール",
    "Duo Collaboration": "デュオコラボ",
    "Power Overload": "パワーオーバーロード",
    "Lonely Journey": "孤独な旅",
    "Electricity Cycle": "電気サイクル",
    "Vehicle Chip: Ice and Fire": "ビークルチップ：氷と炎",
    "Vehicle Chip: Power of Flame": "ビークルチップ：炎の力",
    "Vehicle Chip: Power of Thunder": "ビークルチップ：雷の力",
    "Vehicle Chip: Counterflow Core": "ビークルチップ：逆流コア",
    "Vehicle Chip: Titmouse": "ビークルチップ：シジュウカラ",
    "Vehicle Chip: Broken Blade": "ビークルチップ：折れた刃",
    "Vehicle Chip: Mid-Autumn": "ビークルチップ：中秋",
    "Vehicle Chip: Infinite": "ビークルチップ：インフィニット",
    "Vehicle Chip: Spring Bud": "ビークルチップ：春の芽吹き",
    "Li-Ning Jiguang Tianxing (Exclusive)": "李寧 疾光天行（限定）",
    "Li-Ning Retro Series (Exclusive)": "李寧 レトロシリーズ（限定）",
    "Li-Ning Jiguang Fengxing (Exclusive)": "李寧 疾光風行（限定）",
}

# ジャンル(英語) -> ジャンル(日本語)。LootBar公式タグAPIの日本語名に基づく。
GENRE_MAP = {
    "Weapon": "銃器",
    "Treasure / treasure chest": "お宝 / 宝箱",
    "Vehicle / Transport Aircraft": "乗り物 / 輸送機",
    "Outfit / Set": "衣装 / セット",
    "Chip / Chip": "チップ",
    "": "不明（カテゴリタグなし）",
}


def translate_genre(genre_en: str) -> str:
    return GENRE_MAP.get(genre_en, genre_en or "不明（カテゴリタグなし）")


def translate_name(name_en: str):
    """
    商品名を日本語化する。
    戻り値: (翻訳後の名前, 未対応語彙が残っているかどうかのフラグ)
    """
    if name_en in SPECIAL_MAP:
        return SPECIAL_MAP[name_en], False

    text = name_en

    # 武器コード表記の正規化（先頭の "Type 81:" 等）
    for en, ja in WEAPON_NORMALIZE.items():
        if text.startswith(en):
            text = ja + text[len(en):]

    # エディション語彙
    for en, ja in EDITION_MAP_ORDERED:
        text = text.replace(en, ja)

    # スキンテーマ名
    for en, ja in FAMILY_MAP_ORDERED:
        text = text.replace(en, ja)

    # タグ
    for en, ja in TAG_MAP_ORDERED:
        text = text.replace(en, ja)

    # 未翻訳の英単語(3文字以上のアルファベット列)が残っていないかチェック
    # 武器コード(型番)は英数字+記号の組み合わせなので、通常の単語とは区別しにくいが
    # 目安として "Edition" "Exclusive" 等の残存語だけ検出する
    leftover_markers = ["Edition", "Exclusive", "Tradeable", "Tradable", "Vol.", "Phase"]
    has_leftover = any(marker in text for marker in leftover_markers)

    return text, has_leftover
