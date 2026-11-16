"""All human-readable text in uk, en, de, fr, zh: UI strings, domain labels, country names."""

import pandas as pd
import pycountry
from babel import Locale
from babel.numbers import format_decimal

LANGUAGES: dict[str, str] = {
    "uk": "Українська",
    "en": "English",
    "de": "Deutsch",
    "fr": "Français",
    "zh": "中文",
}
DEFAULT_LANG = "uk"
LANG_INDEX: dict[str, int] = {lang: i for i, lang in enumerate(LANGUAGES)}

# Every entry holds one translation per language, in LANGUAGES order.
TEXTS: dict[str, tuple[str, str, str, str, str]] = {
    "page_title": ("Підбір країни", "Country Matcher", "Länderfinder", "Choix du pays", "国家匹配"),
    "subtitle": (
        "Бал 0–100 показує, наскільки країна близька до вашого ідеалу. Налаштуйте пріоритети на бічній панелі.",
        "A 0–100 score shows how close each country is to your ideal. Set your priorities in the sidebar.",
        "Die Punktzahl 0–100 zeigt, wie nah ein Land Ihrem Ideal kommt. Legen Sie Ihre Prioritäten in der "
        "Seitenleiste fest.",
        "Le score de 0 à 100 indique à quel point chaque pays est proche de votre idéal. Réglez vos priorités "
        "dans le panneau latéral.",
        "0–100分表示每个国家与您理想的接近程度。请在侧边栏设置您的优先事项。",
    ),
    "language": ("Мова", "Language", "Sprache", "Langue", "语言"),
    "mode": ("Режим", "Mode", "Modus", "Mode", "模式"),
    "mode.best": ("Найкраща", "Best overall", "Insgesamt am besten", "Meilleur global", "综合最佳"),
    "mode.ideal": ("Мій ідеал", "My ideal", "Mein Ideal", "Mon idéal", "我的理想"),
    "mode.similar": (
        "Схожі на країну", "Similar to a country", "Ähnlich wie ein Land",
        "Semblable à un pays", "与某国相似",
    ),
    "presets": ("Готові профілі", "Ready-made profiles", "Fertige Profile", "Profils prédéfinis", "预设方案"),
    "weights": (
        "Важливість категорій", "Category importance", "Wichtigkeit der Kategorien",
        "Importance des catégories", "类别重要性",
    ),
    "uniform_note": (
        "У цьому режимі всі показники мають рівну вагу.",
        "In this mode all indicators have equal weight.",
        "In diesem Modus sind alle Indikatoren gleich gewichtet.",
        "Dans ce mode, tous les indicateurs ont le même poids.",
        "此模式下所有指标权重相同。",
    ),
    "desired": ("Бажаний рівень", "Desired level", "Gewünschtes Niveau", "Niveau souhaité", "期望水平"),
    "ref_country": ("Країна-зразок", "Reference country", "Referenzland", "Pays de référence", "参照国家"),
    "fine_tune": (
        "Тонке налаштування показників", "Fine-tune indicators", "Indikatoren feinjustieren",
        "Réglage fin des indicateurs", "指标微调",
    ),
    "fine_tune_note": (
        "Множник ваги показника всередині його категорії.",
        "Weight multiplier for an indicator within its category.",
        "Gewichtungsfaktor eines Indikators innerhalb seiner Kategorie.",
        "Multiplicateur de poids d'un indicateur au sein de sa catégorie.",
        "指标在其类别内的权重系数。",
    ),
    "filters": ("Фільтри", "Filters", "Filter", "Filtres", "筛选"),
    "regions": ("Регіони", "Regions", "Regionen", "Régions", "地区"),
    "all_regions": ("Усі регіони", "All regions", "Alle Regionen", "Toutes les régions", "所有地区"),
    "complete_only": (
        "Лише країни з повними даними", "Only countries with complete data",
        "Nur Länder mit vollständigen Daten", "Uniquement les pays aux données complètes",
        "仅显示数据完整的国家",
    ),
    "refresh": (
        "Оновити дані зі Світового банку", "Refresh World Bank data",
        "Weltbank-Daten aktualisieren", "Actualiser les données de la Banque mondiale",
        "从世界银行更新数据",
    ),
    "refresh_error": (
        "Не вдалося завантажити дані зі Світового банку. Перевірте з'єднання з інтернетом.",
        "Could not download World Bank data. Check your internet connection.",
        "Die Weltbank-Daten konnten nicht geladen werden. Prüfen Sie Ihre Internetverbindung.",
        "Impossible de télécharger les données de la Banque mondiale. Vérifiez votre connexion internet.",
        "无法下载世界银行数据，请检查网络连接。",
    ),
    "demo_data": (
        "Демо-дані: натисніть «Оновити дані зі Світового банку», щоб отримати реальні.",
        "Demo data: click “Refresh World Bank data” to load real figures.",
        "Demodaten: Klicken Sie auf „Weltbank-Daten aktualisieren“, um echte Werte zu laden.",
        "Données de démonstration : cliquez sur « Actualiser les données de la Banque mondiale » "
        "pour charger les vraies valeurs.",
        "演示数据：点击“从世界银行更新数据”以加载真实数据。",
    ),
    "no_results": (
        "Немає результатів: задайте ненульову вагу хоча б одній категорії або розширте фільтр регіонів.",
        "No results: give at least one category a non-zero weight or widen the region filter.",
        "Keine Ergebnisse: Geben Sie mindestens einer Kategorie ein Gewicht über null "
        "oder erweitern Sie den Regionenfilter.",
        "Aucun résultat : donnez un poids non nul à au moins une catégorie ou élargissez le filtre "
        "des régions.",
        "没有结果：请至少为一个类别设置非零权重，或放宽地区筛选。",
    ),
    "weakest": (
        "Найбільше відстає: {reasons}", "Weakest areas: {reasons}", "Größte Schwächen: {reasons}",
        "Points les plus faibles : {reasons}", "最薄弱的方面：{reasons}",
    ),
    "tab.rank": ("Рейтинг", "Ranking", "Rangliste", "Classement", "排名"),
    "tab.compare": ("Порівняння", "Comparison", "Vergleich", "Comparaison", "比较"),
    "tab.map": ("Карта", "Map", "Karte", "Carte", "地图"),
    "tab.explore": ("Огляд", "Explore", "Erkunden", "Explorer", "探索"),
    "explore.x": ("Горизонтальна вісь", "Horizontal axis", "Horizontale Achse", "Axe horizontal", "横轴"),
    "explore.y": ("Вертикальна вісь", "Vertical axis", "Vertikale Achse", "Axe vertical", "纵轴"),
    "explore.note": (
        "Кожна точка — країна: положення показує її рівень у двох категоріях (0–100, відносно інших "
        "країн), колір — бал за вашими налаштуваннями.",
        "Each dot is a country: its position shows its level in two categories (0–100, relative to other "
        "countries), its colour the score for your settings.",
        "Jeder Punkt ist ein Land: Die Position zeigt sein Niveau in zwei Kategorien (0–100, relativ zu "
        "anderen Ländern), die Farbe die Punktzahl für Ihre Einstellungen.",
        "Chaque point est un pays : sa position indique son niveau dans deux catégories (0–100, par rapport "
        "aux autres pays), sa couleur le score selon vos réglages.",
        "每个点代表一个国家：位置表示其在两个类别中的水平（0–100，相对于其他国家），颜色表示按您设置计算的得分。",
    ),
    "col.country": ("Країна", "Country", "Land", "Pays", "国家"),
    "col.region": ("Регіон", "Region", "Region", "Région", "地区"),
    "col.score": ("Бал", "Score", "Punktzahl", "Score", "得分"),
    "col.indicator": ("Показник", "Indicator", "Indikator", "Indicateur", "指标"),
    "col.leader": ("Лідер", "Leader", "Spitzenreiter", "Leader", "第一名"),
    "col.gap": ("Різниця", "Gap", "Differenz", "Écart", "差距"),
    "compare_pick": (
        "Країни для порівняння (до 3)", "Countries to compare (up to 3)",
        "Länder zum Vergleich (bis zu 3)", "Pays à comparer (jusqu'à 3)", "要比较的国家（最多3个）",
    ),
    "compare_limit": (
        "Можна порівняти не більше 3 країн — показано перші три.",
        "You can compare up to 3 countries — showing the first three.",
        "Es lassen sich höchstens 3 Länder vergleichen – die ersten drei werden angezeigt.",
        "Vous pouvez comparer 3 pays au maximum — les trois premiers sont affichés.",
        "最多可比较3个国家，仅显示前三个。",
    ),
    "choose": ("Оберіть…", "Choose…", "Auswählen…", "Choisir…", "请选择…"),
    "why_not.title": (
        "Чому не X, а {winner}?", "Why {winner} and not X?", "Warum {winner} und nicht X?",
        "Pourquoi {winner} et pas X ?", "为什么是{winner}而不是X？",
    ),
    "why_not.pick": ("Країна X", "Country X", "Land X", "Pays X", "国家X"),
    "why_not.summary": (
        "**{other}** — {other_score}, **{winner}** — {winner_score}. Праворуч показники, де {other} "
        "втрачає більше балів, ліворуч — де менше.",
        "**{other}** scores {other_score}, **{winner}** {winner_score}. Bars to the right show where "
        "{other} loses more points, bars to the left where it loses fewer.",
        "**{other}** erreicht {other_score}, **{winner}** {winner_score}. Balken nach rechts zeigen, wo "
        "{other} mehr Punkte verliert, Balken nach links, wo weniger.",
        "**{other}** obtient {other_score}, **{winner}** {winner_score}. Les barres à droite montrent où "
        "{other} perd plus de points, celles à gauche où il en perd moins.",
        "**{other}**得{other_score}分，**{winner}**得{winner_score}分。向右的条形表示{other}失分更多的指标，"
        "向左的表示失分更少的指标。",
    ),
    "why_not.details": (
        "Детальніше за показниками", "Details by indicator", "Details nach Indikator", "Détail par indicateur",
        "按指标查看详情",
    ),
    "chart.points_lost": (
        "Втрачено балів до ідеалу", "Points lost vs. the ideal", "Verlorene Punkte zum Ideal",
        "Points perdus par rapport à l'idéal", "与理想相比失去的分数",
    ),
    "chart.gap_axis": (
        "Різниця втрачених балів: {other} − {winner}", "Difference in points lost: {other} − {winner}",
        "Differenz der verlorenen Punkte: {other} − {winner}", "Écart de points perdus : {other} − {winner}",
        "失分差：{other} − {winner}",
    ),
    "chart.ideal": ("Ідеал", "Ideal", "Ideal", "Idéal", "理想"),
    "values.title": ("Реальні значення", "Actual values", "Tatsächliche Werte", "Valeurs réelles", "实际数值"),
    "values.note": (
        "У дужках — рік останніх доступних даних.", "The year of the latest available data is in brackets.",
        "In Klammern: Jahr der neuesten verfügbaren Daten.",
        "Entre parenthèses : année des dernières données disponibles.", "括号内为最新可用数据的年份。",
    ),
    "download": (
        "Завантажити рейтинг (CSV)", "Download ranking (CSV)", "Rangliste herunterladen (CSV)",
        "Télécharger le classement (CSV)", "下载排名（CSV）",
    ),
    "share": ("Поділитися", "Share", "Teilen", "Partager", "分享"),
    "share.note": (
        "Посилання відкриє застосунок з такими самими налаштуваннями.",
        "This link opens the app with the same settings.",
        "Dieser Link öffnet die App mit denselben Einstellungen.",
        "Ce lien ouvre l'application avec les mêmes réglages.", "此链接将以相同设置打开应用。",
    ),
    # Preference quiz: UI
    "quiz.open": (
        "Не знаєте, що обрати? Міні-тест на 1 хвилину", "Not sure? Take the 1-minute quiz",
        "Unsicher? Machen Sie den 1-Minuten-Test", "Indécis ? Faites le quiz d'une minute", "拿不定主意？做个1分钟小测试",
    ),
    "quiz.title": ("Міні-тест", "Quick quiz", "Kurztest", "Mini-quiz", "快速测试"),
    "quiz.intro": (
        "{n} буденних ситуацій. Обирайте, що ближче, а якщо не знаєте — просто пропускайте.",
        "{n} everyday situations. Pick what feels closest, or simply skip if you're not sure.",
        "{n} Alltagssituationen. Wählen Sie, was am besten passt, oder überspringen Sie einfach.",
        "{n} situations du quotidien. Choisissez ce qui vous ressemble, ou passez si vous hésitez.",
        "{n}个日常情境。选最接近您的答案，拿不准就直接跳过。",
    ),
    "quiz.progress": (
        "Питання {i} з {n}", "Question {i} of {n}", "Frage {i} von {n}", "Question {i} sur {n}", "第{i}题，共{n}题",
    ),
    "quiz.skip": ("Пропустити", "Skip", "Überspringen", "Passer", "跳过"),
    "quiz.back": ("Назад", "Back", "Zurück", "Retour", "上一步"),
    "quiz.restart": ("Почати знову", "Start over", "Neu starten", "Recommencer", "重新开始"),
    "quiz.result_title": (
        "🎉 Ваш профіль готовий", "🎉 Your profile is ready", "🎉 Ihr Profil ist fertig", "🎉 Votre profil est prêt",
        "🎉 您的偏好已生成",
    ),
    "quiz.result_answered": (
        "Відповідей: {answered} з {n}. Пропущені питання на результат не впливають.",
        "Answered {answered} of {n}. Skipped questions don't affect the result.",
        "{answered} von {n} beantwortet. Übersprungene Fragen beeinflussen das Ergebnis nicht.",
        "{answered} réponses sur {n}. Les questions passées n'influencent pas le résultat.",
        "已回答{answered}/{n}题。跳过的问题不影响结果。",
    ),
    "quiz.all_skipped": (
        "Ви пропустили всі питання, тож усі критерії отримають однакову вагу.",
        "You skipped every question, so all criteria get equal weight.",
        "Sie haben alle Fragen übersprungen, daher werden alle Kriterien gleich gewichtet.",
        "Vous avez passé toutes les questions : tous les critères auront le même poids.",
        "您跳过了所有问题，所有标准将获得相同权重。",
    ),
    "quiz.apply": ("Показати мої країни", "Show my countries", "Meine Länder anzeigen", "Voir mes pays", "查看我的国家"),
    "quiz.done": (
        "Ваги розраховано за тестом. Найважливіше для вас: {cats}.",
        "Weights calculated from the quiz. What matters most to you: {cats}.",
        "Gewichte aus dem Test berechnet. Am wichtigsten ist Ihnen: {cats}.",
        "Poids calculés d'après le quiz. Ce qui compte le plus pour vous : {cats}.",
        "已根据测试计算权重。您最看重的是：{cats}。",
    ),
    # Preference quiz: scenarios (keyed by quiz.QUESTIONS ids) and their options
    "quiz.weekend": (
        "Вільна субота. Як ви її проведете?", "A free Saturday. How do you spend it?",
        "Ein freier Samstag. Wie verbringen Sie ihn?", "Un samedi libre. Comment le passez-vous ?",
        "空闲的周六，您会怎么过？",
    ),
    "quiz.weekend.nature": (
        "Похід у ліс або в гори", "Hiking in the woods or mountains", "Wandern im Wald oder in den Bergen",
        "Randonnée en forêt ou en montagne", "去森林或山里徒步",
    ),
    "quiz.weekend.city": (
        "Кав'ярні та нові місця в місті", "Cafés and new spots in town", "Cafés und neue Orte in der Stadt",
        "Cafés et nouveaux lieux en ville", "逛城里的咖啡馆和新去处",
    ),
    "quiz.weekend.family": (
        "Спокійний день у парку з рідними", "A calm day in the park with family",
        "Ein ruhiger Tag im Park mit der Familie", "Une journée tranquille au parc en famille", "和家人在公园度过平静的一天",
    ),
    "quiz.night": (
        "23:00, ви йдете додому пішки. Що відчуваєте?", "11 pm, you're walking home. How do you feel?",
        "23 Uhr, Sie gehen zu Fuß nach Hause. Wie fühlen Sie sich?", "23 h, vous rentrez à pied. Que ressentez-vous ?",
        "晚上11点，您步行回家。感觉如何？",
    ),
    "quiz.night.calm": (
        "Хочу почуватися абсолютно спокійно", "I want to feel completely at ease", "Ich will mich völlig sicher fühlen",
        "Je veux me sentir parfaitement serein(e)", "我希望完全安心",
    ),
    "quiz.night.alert": (
        "Трохи пильності — це нормально", "A little caution is fine", "Ein bisschen Vorsicht ist okay",
        "Un peu de vigilance, ça va", "稍加小心就好",
    ),
    "quiz.night.fearless": (
        "Я про таке навіть не думаю", "I don't even think about it", "Darüber denke ich gar nicht nach",
        "Je n'y pense même pas", "我根本不考虑这些",
    ),
    "quiz.wallet": (
        "Перший місяць на новому місці. Що порадує найбільше?",
        "Your first month in a new place. What would make you happiest?",
        "Ihr erster Monat am neuen Ort. Was würde Sie am meisten freuen?",
        "Votre premier mois dans un nouvel endroit. Qu'est-ce qui vous ferait le plus plaisir ?",
        "在新地方的第一个月，什么最让您开心？",
    ),
    "quiz.wallet.salary": ("Солідна зарплата", "A solid paycheck", "Ein ordentliches Gehalt", "Un bon salaire", "可观的薪水"),
    "quiz.wallet.job": (
        "Знайти роботу за тиждень", "Landing a job within a week", "In einer Woche einen Job finden",
        "Trouver un emploi en une semaine", "一周内找到工作",
    ),
    "quiz.wallet.cheap": (
        "Ціни, що приємно дивують", "Prices that pleasantly surprise me", "Preise, die angenehm überraschen",
        "Des prix qui surprennent agréablement", "物价让人惊喜",
    ),
    "quiz.doctor": (
        "Ви застудилися. Що для вас головне?", "You've caught a cold. What matters most?",
        "Sie sind erkältet. Was ist Ihnen am wichtigsten?", "Vous avez attrapé un rhume. Qu'est-ce qui compte le plus ?",
        "您感冒了，什么最重要？",
    ),
    "quiz.doctor.clinic": (
        "Хороший лікар уже завтра", "A good doctor by tomorrow", "Schon morgen ein guter Arzt",
        "Un bon médecin dès demain", "明天就能看上好医生",
    ),
    "quiz.doctor.prevention": (
        "Я рідко хворію — дбаю про здоров'я наперед", "I rarely get sick: prevention first",
        "Ich werde selten krank: Vorsorge zuerst", "Je tombe rarement malade : la prévention d'abord", "我很少生病，重在预防",
    ),
    "quiz.doctor.tea": (
        "Чай з лимоном — і все минеться", "Tea with lemon and it'll pass", "Tee mit Zitrone, dann geht's vorbei",
        "Un thé au citron et ça passera", "喝杯柠檬茶就好了",
    ),
    "quiz.paperwork": (
        "Треба оформити документи в держустанові. Чого хочеться?",
        "You need paperwork from a government office. What do you hope for?",
        "Sie brauchen Unterlagen vom Amt. Was wünschen Sie sich?",
        "Vous avez une démarche administrative. Qu'espérez-vous ?", "您需要去政府部门办手续，您希望怎样？",
    ),
    "quiz.paperwork.honest": (
        "Чесно, за правилами, без «подяк»", "Honest, by the rules, no 'gifts'", "Ehrlich, nach Regeln, ohne „Geschenke“",
        "Honnête, dans les règles, sans « cadeaux »", "按规矩办事，不用“打点”",
    ),
    "quiz.paperwork.stable": (
        "Щоб правила не змінювались щороку", "Rules that don't change every year",
        "Regeln, die sich nicht jedes Jahr ändern", "Des règles qui ne changent pas chaque année", "规则不要年年变",
    ),
    "quiz.paperwork.whatever": (
        "Якось розберуся", "I'll figure it out", "Ich komme schon zurecht", "Je me débrouillerai", "总能搞定",
    ),
    "quiz.online": (
        "Без чого не обійдеться ваш день?", "What can't your day do without?", "Worauf kann Ihr Tag nicht verzichten?",
        "De quoi votre journée ne peut-elle pas se passer ?", "您的一天离不开什么？",
    ),
    "quiz.online.wifi": (
        "Швидкий інтернет — я працюю онлайн", "Fast internet: I work online", "Schnelles Internet: Ich arbeite online",
        "Un internet rapide : je travaille en ligne", "高速网络，我在线工作",
    ),
    "quiz.online.calls": (
        "Відеодзвінки з рідними час від часу", "Video calls with family now and then",
        "Ab und zu Videoanrufe mit der Familie", "Des appels vidéo avec la famille de temps en temps", "偶尔和家人视频通话",
    ),
    "quiz.online.offline": (
        "Книжка і жодних сповіщень", "A book and no notifications", "Ein Buch und keine Benachrichtigungen",
        "Un livre et aucune notification", "一本书，没有任何通知",
    ),
    "quiz.dream": (
        "Країна мрії — це…", "Your dream country is…", "Ihr Traumland ist…", "Votre pays de rêve, c'est…",
        "您理想中的国家是……",
    ),
    "quiz.dream.best": (
        "Найкраща в усіх рейтингах", "Top of every ranking", "Spitze in jedem Ranking",
        "En tête de tous les classements", "各项排名都名列前茅",
    ),
    "quiz.dream.balanced": (
        "Добра, але без крайнощів", "Good, nothing extreme", "Gut, ohne Extreme", "Bien, sans excès", "不错就行，不求极致",
    ),
    "quiz.dream.reachable": (
        "Скромніша, зате реальна для переїзду", "More modest, but within reach", "Bescheidener, aber erreichbar",
        "Plus modeste, mais accessible", "条件一般，但更容易实现",
    ),
    # Categories
    "cat.safety": ("Безпека", "Safety", "Sicherheit", "Sécurité", "安全"),
    "cat.economy": ("Економіка", "Economy", "Wirtschaft", "Économie", "经济"),
    "cat.health": ("Здоров'я", "Health", "Gesundheit", "Santé", "健康"),
    "cat.environment": ("Довкілля", "Environment", "Umwelt", "Environnement", "环境"),
    "cat.governance": ("Врядування", "Governance", "Regierungsführung", "Gouvernance", "治理"),
    "cat.digital": ("Цифровізація", "Digital", "Digitalisierung", "Numérique", "数字化"),
    # Indicators (keyed by config.INDICATORS codes)
    "ind.WB_WDI_VC_IHR_PSRC_P5": (
        "Умисні вбивства на 100 тис.", "Intentional homicides per 100k",
        "Vorsätzliche Tötungen je 100.000", "Homicides volontaires pour 100 000", "每10万人故意杀人数",
    ),
    "ind.WB_WGI_PV_EST": (
        "Політична стабільність", "Political stability", "Politische Stabilität",
        "Stabilité politique", "政治稳定",
    ),
    "ind.WB_WDI_NY_GDP_PCAP_PP_CD": (
        "ВВП на душу (ПКС, $)", "GDP per capita (PPP, $)", "BIP pro Kopf (KKP, $)",
        "PIB par habitant (PPA, $)", "人均GDP（购买力平价，美元）",
    ),
    "ind.WB_WDI_SL_UEM_TOTL_ZS": ("Безробіття, %", "Unemployment, %", "Arbeitslosigkeit, %", "Chômage, %", "失业率，%"),
    "ind.WB_WDI_FP_CPI_TOTL_ZG": ("Інфляція, %", "Inflation, %", "Inflation, %", "Inflation, %", "通货膨胀率，%"),
    "ind.WB_WDI_SP_DYN_LE00_IN": (
        "Очікувана тривалість життя", "Life expectancy", "Lebenserwartung", "Espérance de vie", "预期寿命",
    ),
    "ind.WB_WDI_SH_XPD_CHEX_PC_CD": (
        "Витрати на охорону здоров'я на душу, $", "Health spending per capita, $",
        "Gesundheitsausgaben pro Kopf, $", "Dépenses de santé par habitant, $", "人均卫生支出，美元",
    ),
    "ind.WB_WDI_EN_ATM_PM25_MC_M3": (
        "Забруднення повітря PM2.5", "Air pollution (PM2.5)", "Luftverschmutzung (PM2,5)",
        "Pollution de l'air (PM2,5)", "空气污染（PM2.5）",
    ),
    "ind.WB_WGI_CC_EST": (
        "Контроль корупції", "Control of corruption", "Korruptionskontrolle",
        "Maîtrise de la corruption", "腐败控制",
    ),
    "ind.WB_WDI_IT_NET_USER_ZS": (
        "Користувачі інтернету, %", "Internet users, %", "Internetnutzer, %", "Internautes, %", "互联网用户，%",
    ),
    # Presets (keyed by their id in presets.py)
    "preset.student": ("Студент", "Student", "Student", "Étudiant", "学生"),
    "preset.remote": (
        "Віддалений працівник", "Remote worker", "Remote-Beschäftigte", "Télétravailleur", "远程工作者",
    ),
    "preset.family": (
        "Сім'я з дітьми", "Family with children", "Familie mit Kindern", "Famille avec enfants",
        "有孩子的家庭",
    ),
    "preset.retiree": ("Пенсіонер", "Retiree", "Rentner", "Retraité", "退休人员"),
    "preset.startup": ("Стартапер", "Startup founder", "Start-up-Gründer", "Fondateur de start-up", "创业者"),
    "preset.it_specialist": ("IT-спеціаліст", "IT specialist", "IT-Fachkraft", "Spécialiste IT", "IT专业人员"),
    "preset.eco": ("Еко-свідомий", "Eco-conscious", "Umweltbewusst", "Écoresponsable", "环保主义者"),
    "preset.job_seeker": ("Шукач роботи", "Job seeker", "Arbeitssuchende", "Demandeur d'emploi", "求职者"),
    "preset.safety_first": (
        "Безпека понад усе", "Safety first", "Sicherheit zuerst", "La sécurité avant tout", "安全第一",
    ),
    "preset.medical": ("Лікування", "Medical care", "Medizinische Versorgung", "Soins médicaux", "医疗"),
    "preset.integrity": (
        "Борець за чесність", "Integrity first", "Integrität zuerst", "L'intégrité avant tout", "廉洁优先",
    ),
    "preset.balanced": ("Збалансований", "Balanced", "Ausgewogen", "Équilibré", "均衡"),
    # World Bank regions (keyed by their English name in the dataset)
    "region.East Asia & Pacific": (
        "Східна Азія і Тихоокеанський регіон", "East Asia & Pacific", "Ostasien und Pazifik",
        "Asie de l'Est et Pacifique", "东亚与太平洋",
    ),
    "region.Europe & Central Asia": (
        "Європа і Центральна Азія", "Europe & Central Asia", "Europa und Zentralasien",
        "Europe et Asie centrale", "欧洲与中亚",
    ),
    "region.Latin America & Caribbean": (
        "Латинська Америка і Карибський басейн", "Latin America & Caribbean",
        "Lateinamerika und Karibik", "Amérique latine et Caraïbes", "拉丁美洲和加勒比",
    ),
    "region.Middle East, North Africa, Afghanistan & Pakistan": (
        "Близький Схід, Північна Африка, Афганістан і Пакистан",
        "Middle East, North Africa, Afghanistan & Pakistan",
        "Naher Osten, Nordafrika, Afghanistan und Pakistan",
        "Moyen-Orient, Afrique du Nord, Afghanistan et Pakistan", "中东、北非、阿富汗和巴基斯坦",
    ),
    "region.Middle East & North Africa": (
        "Близький Схід і Північна Африка", "Middle East & North Africa", "Naher Osten und Nordafrika",
        "Moyen-Orient et Afrique du Nord", "中东和北非",
    ),
    "region.North America": ("Північна Америка", "North America", "Nordamerika", "Amérique du Nord", "北美"),
    "region.South Asia": ("Південна Азія", "South Asia", "Südasien", "Asie du Sud", "南亚"),
    "region.Sub-Saharan Africa": (
        "Африка на південь від Сахари", "Sub-Saharan Africa", "Subsahara-Afrika",
        "Afrique subsaharienne", "撒哈拉以南非洲",
    ),
    # Economies without an ISO 3166 / CLDR entry
    "country.CHI": ("Нормандські острови", "Channel Islands", "Kanalinseln", "Îles Anglo-Normandes", "海峡群岛"),
}

ALPHA2_OVERRIDES: dict[str, str] = {"XKX": "XK"}  # World Bank code -> CLDR territory


def t(key: str, lang: str, **fmt: object) -> str:
    """Translated text for `key`, with `{placeholders}` filled from `fmt`."""
    text = TEXTS[key][LANG_INDEX[lang]]
    return text.format(**fmt) if fmt else text


def label(prefix: str, name: str, lang: str) -> str:
    """Translated name of a category/indicator/preset/region; unknown regions stay as-is."""
    key = f"{prefix}.{name}"
    return t(key, lang) if key in TEXTS else name


def format_number(value: float, lang: str) -> str:
    """Locale-formatted number; fewer decimals for larger magnitudes (54 210, 74.7, -0.33)."""
    pattern = "#,##0" if abs(value) >= 100 else "#,##0.#" if abs(value) >= 10 else "#,##0.##"
    return format_decimal(value, format=pattern, locale=lang)


def _alpha2(iso3: str) -> str | None:
    """ISO alpha-2 code used by CLDR for a World Bank iso3 code."""
    if iso3 in ALPHA2_OVERRIDES:
        return ALPHA2_OVERRIDES[iso3]
    country = pycountry.countries.get(alpha_3=iso3)
    return country.alpha_2 if country else None


def country_names(fallback: pd.Series, lang: str) -> pd.Series:
    """Country names in `lang` (CLDR), indexed by iso3; `fallback` covers unknown codes."""
    territories = Locale.parse(lang).territories

    def name(iso3: str) -> str:
        if f"country.{iso3}" in TEXTS:
            return t(f"country.{iso3}", lang)
        return territories.get(_alpha2(iso3) or "", fallback[iso3])

    return pd.Series({iso3: name(iso3) for iso3 in fallback.index}, name="country")
