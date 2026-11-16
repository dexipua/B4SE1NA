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
    "es": "Español",
    "it": "Italiano",
    "pt": "Português",
    "pl": "Polski",
    "nl": "Nederlands",
    "cs": "Čeština",
    "tr": "Türkçe",
    "ja": "日本語",
    "ko": "한국어",
    "hi": "हिन्दी",
}
DEFAULT_LANG = "uk"
LANG_INDEX: dict[str, int] = {lang: i for i, lang in enumerate(LANGUAGES)}

# Every entry holds one translation per language, in LANGUAGES order.
TEXTS: dict[str, tuple[str, str, str, str, str]] = {
    "page_title": ("Підбір країни", "Country Matcher", "Länderfinder", "Choix du pays", "国家匹配", "Selector de país", "Scelta del paese", "Escolha do país", "Dobór kraju", "Landenkiezer", "Výběr země", "Ülke Seçici", "国選びツール", "국가 매칭", "देश चयनकर्ता"),
    "subtitle": (
        "Бал 0–100 показує, наскільки країна близька до вашого ідеалу. Налаштуйте пріоритети на бічній панелі.",
        "A 0–100 score shows how close each country is to your ideal. Set your priorities in the sidebar.",
        "Die Punktzahl 0–100 zeigt, wie nah ein Land Ihrem Ideal kommt. Legen Sie Ihre Prioritäten in der "
        "Seitenleiste fest.",
        "Le score de 0 à 100 indique à quel point chaque pays est proche de votre idéal. Réglez vos priorités "
        "dans le panneau latéral.",
        "0–100分表示每个国家与您理想的接近程度。请在侧边栏设置您的优先事项。",
        "La puntuación de 0 a 100 indica lo cerca que está cada país de su ideal. "
        "Defina sus prioridades en la barra lateral.",
        "Il punteggio da 0 a 100 indica quanto ogni paese si avvicina al tuo ideale. "
        "Imposta le tue priorità nella barra laterale.",
        "A pontuação de 0 a 100 mostra o quão perto cada país está do seu ideal. "
        "Defina as suas prioridades na barra lateral.",
        "Wynik od 0 do 100 pokazuje, jak blisko ideału jest dany kraj. "
        "Ustaw swoje priorytety na panelu bocznym.",
        "De score van 0–100 laat zien hoe dicht elk land bij jouw ideaal komt. "
        "Stel je prioriteiten in via de zijbalk.",
        "Skóre 0–100 ukazuje, jak blízko má každá země k vašemu ideálu. "
        "Nastavte své priority v postranním panelu.",
        "0–100 arası puan, her ülkenin idealinize ne kadar yakın olduğunu gösterir. "
        "Önceliklerinizi kenar çubuğundan ayarlayın.",
        "0〜100のスコアは、各国があなたの理想にどれだけ近いかを示します。"
        "サイドバーで優先事項を設定してください。",
        "0–100점은 각 국가가 이상에 얼마나 가까운지를 나타냅니다. 사이드바에서 우선순위를 설정하세요.",
        "0–100 का स्कोर बताता है कि हर देश आपके आदर्श के कितना करीब है। "
        "साइडबार में अपनी प्राथमिकताएँ तय करें।",
    ),
    "language": ("Мова", "Language", "Sprache", "Langue", "语言", "Idioma", "Lingua", "Idioma", "Język", "Taal", "Jazyk", "Dil", "言語", "언어", "भाषा"),
    "mode": ("Режим", "Mode", "Modus", "Mode", "模式", "Modo", "Modalità", "Modo", "Tryb", "Modus", "Režim", "Mod", "モード", "모드", "मोड"),
    "mode.best": ("Найкраща", "Best overall", "Insgesamt am besten", "Meilleur global", "综合最佳",  "Mejor en general", "Migliore in assoluto", "Melhor no geral", "Najlepszy ogółem", "Beste overall", "Celkově nejlepší", "Genel olarak en iyi", "総合ベスト", "종합 최고", "कुल मिलाकर सर्वश्रेष्ठ",),
    "mode.ideal": ("Мій ідеал", "My ideal", "Mein Ideal", "Mon idéal", "我的理想", "Mi ideal", "Il mio ideale", "O meu ideal", "Mój ideał", "Mijn ideaal", "Můj ideál", "İdealim", "私の理想", "나의 이상", "मेरा आदर्श",),
    "mode.similar": ("Схожі на країну", "Similar to a country", "Ähnlich wie ein Land", "Semblable à un pays", "与某国相似", "Parecido a un país", "Simile a un paese", "Semelhante a um país", "Podobny do kraju", "Vergelijkbaar met een land", "Podobné určité zemi", "Bir ülkeye benzer", "ある国に似た国", "특정 국가와 유사", "किसी देश जैसा",),
    "presets": ("Готові профілі", "Ready-made profiles", "Fertige Profile", "Profils prédéfinis", "预设方案", "Perfiles predefinidos", "Profili predefiniti", "Perfis predefinidos", "Gotowe profile", "Kant-en-klare profielen", "Hotové profily", "Hazır profiller", "プリセット", "미리 정의된 프로필", "तैयार प्रोफ़ाइल",),
    "weights": ("Важливість категорій", "Category importance", "Wichtigkeit der Kategorien","Importance des catégories", "类别重要性", "Importancia de las categorías", "Importanza delle categorie", "Importância das categorias","Ważność kategorii", "Belang van categorieën", "Důležitost kategorií", "Kategorilerin önemi", "カテゴリの重要度", "카테고리 중요도", "श्रेणियों का महत्व",),
    "uniform_note": (
        "У цьому режимі всі показники мають рівну вагу.",
        "In this mode all indicators have equal weight.",
        "In diesem Modus sind alle Indikatoren gleich gewichtet.",
        "Dans ce mode, tous les indicateurs ont le même poids.",
        "此模式下所有指标权重相同。",
        "En este modo todos los indicadores tienen el mismo peso.",
        "In questa modalità tutti gli indicatori hanno lo stesso peso.",
        "Neste modo, todos os indicadores têm o mesmo peso.",
        "W tym trybie wszystkie wskaźniki mają jednakową wagę.",
        "In deze modus hebben alle indicatoren hetzelfde gewicht.",
        "V tomto režimu mají všechny ukazatele stejnou váhu.",
        "Bu modda tüm göstergelerin ağırlığı eşittir.",
        "このモードでは、すべての指標が同じ重みになります。",
        "이 모드에서는 모든 지표의 가중치가 같습니다.",
        "इस मोड में सभी संकेतकों का भार समान होता है।",
    ),
    "desired": ("Бажаний рівень", "Desired level", "Gewünschtes Niveau", "Niveau souhaité", "期望水平", "Nivel deseado", "Livello desiderato", "Nível desejado", "Pożądany poziom", "Gewenst niveau","Požadovaná úroveň", "İstenen düzey", "希望水準", "희망 수준", "वांछित स्तर",),
    "ref_country": ("Країна-зразок", "Reference country", "Referenzland", "Pays de référence", "参照国家", "País de referencia", "Paese di riferimento", "País de referência", "Kraj odniesienia","Referentieland", "Referenční země", "Referans ülke", "基準となる国", "기준 국가", "संदर्भ देश",),
    "fine_tune": (
        "Тонке налаштування показників", "Fine-tune indicators", "Indikatoren feinjustieren",
        "Réglage fin des indicateurs", "指标微调", "Ajuste fino de indicadores", "Regolazione fine degli indicatori", "Ajuste fino dos indicadores",
        "Dokładne dostrojenie wskaźników", "Indicatoren verfijnen", "Jemné doladění ukazatelů",
        "Göstergelerde ince ayar", "指標の微調整", "지표 미세 조정", "संकेतकों का बारीक समायोजन",
    ),
    "fine_tune_note": (
        "Множник ваги показника всередині його категорії.",
        "Weight multiplier for an indicator within its category.",
        "Gewichtungsfaktor eines Indikators innerhalb seiner Kategorie.",
        "Multiplicateur de poids d'un indicateur au sein de sa catégorie.",
        "指标在其类别内的权重系数。",
        "Multiplicador de peso de un indicador dentro de su categoría.",
        "Moltiplicatore del peso di un indicatore all'interno della sua categoria.",
        "Multiplicador de peso de um indicador dentro da sua categoria.",
        "Mnożnik wagi wskaźnika w obrębie jego kategorii.",
        "Gewichtsmultiplicator van een indicator binnen zijn categorie.",
        "Násobitel váhy ukazatele v rámci jeho kategorie.",
        "Bir göstergenin kendi kategorisi içindeki ağırlık çarpanı.",
        "カテゴリ内での指標の重み係数です。",
        "카테고리 내에서 지표에 적용되는 가중치 배수입니다.",
        "किसी संकेतक की अपनी श्रेणी के भीतर भार का गुणक।",
    ),
    "filters": ("Фільтри", "Filters", "Filter", "Filtres", "筛选", "Filtros", "Filtri", "Filtros", "Filtry", "Filters", "Filtry", "Filtreler", "フィルター","필터", "फ़िल्टर",),
    "regions": ("Регіони", "Regions", "Regionen", "Régions", "地区", "Regiones", "Regioni", "Regiões", "Regiony", "Regio's", "Regiony", "Bölgeler", "地域","지역", "क्षेत्र",),
    "all_regions": ("Усі регіони", "All regions", "Alle Regionen", "Toutes les régions", "所有地区", "Todas las regiones", "Tutte le regioni", "Todas as regiões", "Wszystkie regiony","Alle regio's", "Všechny regiony", "Tüm bölgeler", "すべての地域", "모든 지역", "सभी क्षेत्र",),
    "complete_only": (
        "Лише країни з повними даними", "Only countries with complete data",
        "Nur Länder mit vollständigen Daten", "Uniquement les pays aux données complètes",
        "仅显示数据完整的国家",
        "Solo países con datos completos", "Solo paesi con dati completi",
        "Apenas países com dados completos", "Tylko kraje z kompletnymi danymi",
        "Alleen landen met volledige gegevens", "Pouze země s úplnými daty",
        "Yalnızca verisi tam olan ülkeler", "データが揃っている国のみ", "데이터가 완전한 국가만",
        "केवल पूर्ण डेटा वाले देश",
    ),
    "refresh": (
        "Оновити дані зі Світового банку", "Refresh World Bank data",
        "Weltbank-Daten aktualisieren", "Actualiser les données de la Banque mondiale",
        "从世界银行更新数据",
        "Actualizar datos del Banco Mundial", "Aggiorna i dati della Banca Mondiale",
        "Atualizar dados do Banco Mundial", "Odśwież dane Banku Światowego",
        "Wereldbankgegevens vernieuwen", "Obnovit data Světové banky",
        "Dünya Bankası verilerini güncelle", "世界銀行のデータを更新", "세계은행 데이터 새로고침",
        "विश्व बैंक का डेटा अपडेट करें",
    ),
    "refresh_error": (
        "Не вдалося завантажити дані зі Світового банку. Перевірте з'єднання з інтернетом.",
        "Could not download World Bank data. Check your internet connection.",
        "Die Weltbank-Daten konnten nicht geladen werden. Prüfen Sie Ihre Internetverbindung.",
        "Impossible de télécharger les données de la Banque mondiale. Vérifiez votre connexion internet.",
        "无法下载世界银行数据，请检查网络连接。",
        "No se pudieron descargar los datos del Banco Mundial. Compruebe su conexión a internet.",
        "Impossibile scaricare i dati della Banca Mondiale. Controlla la connessione a internet.",
        "Não foi possível transferir os dados do Banco Mundial. Verifique a sua ligação à internet.",
        "Nie udało się pobrać danych Banku Światowego. Sprawdź połączenie z internetem.",
        "De gegevens van de Wereldbank konden niet worden gedownload. Controleer je internetverbinding.",
        "Data Světové banky se nepodařilo stáhnout. Zkontrolujte připojení k internetu.",
        "Dünya Bankası verileri indirilemedi. İnternet bağlantınızı kontrol edin.",
        "世界銀行のデータをダウンロードできませんでした。インターネット接続を確認してください。",
        "세계은행 데이터를 다운로드하지 못했습니다. 인터넷 연결을 확인하세요.",
        "विश्व बैंक का डेटा डाउनलोड नहीं हो सका। अपना इंटरनेट कनेक्शन जाँचें।",
    ),
    "demo_data": (
        "Демо-дані: натисніть «Оновити дані зі Світового банку», щоб отримати реальні.",
        "Demo data: click “Refresh World Bank data” to load real figures.",
        "Demodaten: Klicken Sie auf „Weltbank-Daten aktualisieren“, um echte Werte zu laden.",
        "Données de démonstration : cliquez sur « Actualiser les données de la Banque mondiale » "
        "pour charger les vraies valeurs.",
        "演示数据：点击“从世界银行更新数据”以加载真实数据。",
        "Datos de demostración: pulse «Actualizar datos del Banco Mundial» para cargar cifras reales.",
        "Dati dimostrativi: fai clic su «Aggiorna i dati della Banca Mondiale» per caricare i valori reali.",
        "Dados de demonstração: clique em «Atualizar dados do Banco Mundial» para carregar valores reais.",
        "Dane demonstracyjne: kliknij „Odśwież dane Banku Światowego”, aby wczytać prawdziwe wartości.",
        "Demogegevens: klik op ‘Wereldbankgegevens vernieuwen’ om echte cijfers te laden.",
        "Ukázková data: kliknutím na „Obnovit data Světové banky“ načtete skutečné hodnoty.",
        "Demo verileri: gerçek değerleri yüklemek için “Dünya Bankası verilerini güncelle” "
        "düğmesine tıklayın.",
        "デモデータです。「世界銀行のデータを更新」をクリックすると実際の数値が読み込まれます。",
        "데모 데이터입니다. 실제 수치를 불러오려면 “세계은행 데이터 새로고침”을 클릭하세요.",
        "डेमो डेटा: वास्तविक आँकड़े लोड करने के लिए “विश्व बैंक का डेटा अपडेट करें” पर क्लिक करें।",
    ),
    "no_results": (
        "Немає результатів: задайте ненульову вагу хоча б одній категорії або розширте фільтр регіонів.",
        "No results: give at least one category a non-zero weight or widen the region filter.",
        "Keine Ergebnisse: Geben Sie mindestens einer Kategorie ein Gewicht über null "
        "oder erweitern Sie den Regionenfilter.",
        "Aucun résultat : donnez un poids non nul à au moins une catégorie ou élargissez le filtre "
        "des régions.",
        "没有结果：请至少为一个类别设置非零权重，或放宽地区筛选。",
        "Sin resultados: asigne un peso distinto de cero al menos a una categoría o amplíe el filtro "
        "de regiones.",
        "Nessun risultato: assegna un peso diverso da zero ad almeno una categoria o amplia il filtro "
        "delle regioni.",
        "Sem resultados: atribua um peso diferente de zero a pelo menos uma categoria ou alargue o "
        "filtro de regiões.",
        "Brak wyników: nadaj co najmniej jednej kategorii wagę większą od zera lub poszerz filtr "
        "regionów.",
        "Geen resultaten: geef minstens één categorie een gewicht groter dan nul of verbreed het "
        "regiofilter.",
        "Žádné výsledky: přidělte alespoň jedné kategorii nenulovou váhu nebo rozšiřte filtr regionů.",
        "Sonuç yok: en az bir kategoriye sıfırdan büyük bir ağırlık verin veya bölge filtresini "
        "genişletin.",
        "結果がありません。少なくとも1つのカテゴリに0より大きい重みを設定するか、地域フィルターを広げてください。",
        "결과가 없습니다. 최소 한 개 카테고리에 0이 아닌 가중치를 주거나 지역 필터를 넓히세요.",
        "कोई परिणाम नहीं: कम से कम एक श्रेणी को शून्य से अधिक भार दें या क्षेत्र फ़िल्टर का दायरा बढ़ाएँ।",
    ),
    "weakest": (
        "Найбільше відстає: {reasons}", "Weakest areas: {reasons}", "Größte Schwächen: {reasons}",
        "Points les plus faibles : {reasons}", "最薄弱的方面：{reasons}", "Puntos más débiles: {reasons}", "Punti più deboli: {reasons}", "Pontos mais fracos: {reasons}",
        "Najsłabsze obszary: {reasons}", "Zwakste punten: {reasons}", "Nejslabší oblasti: {reasons}",
        "En zayıf alanlar: {reasons}", "最も弱い分野：{reasons}", "가장 약한 부분: {reasons}",
        "सबसे कमज़ोर क्षेत्र: {reasons}",
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

    "tab.rank": ("Рейтинг", "Ranking", "Rangliste", "Classement", "排名", "Clasificación", "Classifica", "Classificação", "Ranking", "Ranglijst", "Žebříček","Sıralama", "ランキング", "순위", "रैंकिंग",),
    "tab.compare": ("Порівняння", "Comparison", "Vergleich", "Comparaison", "比较", "Comparación", "Confronto", "Comparação", "Porównanie", "Vergelijking", "Srovnání","Karşılaştırma", "比較", "비교", "तुलना",),
    "tab.map": ("Карта", "Map", "Karte", "Carte", "地图", "Mapa", "Mappa", "Mapa", "Mapa", "Kaart", "Mapa", "Harita", "地図", "지도", "नक्शा"),
    "col.country": ("Країна", "Country", "Land", "Pays", "国家", "País", "Paese", "País", "Kraj", "Land", "Země", "Ülke", "国", "국가", "देश"),
    "col.region": ("Регіон", "Region", "Region", "Région", "地区", "Región", "Regione", "Região", "Region", "Regio", "Region", "Bölge", "地域", "지역", "क्षेत्र",),
    "col.score": ("Бал", "Score", "Punktzahl", "Score", "得分",  "Puntuación", "Punteggio", "Pontuação", "Wynik", "Score", "Skóre", "Puan", "スコア", "점수","स्कोर",),
    "col.indicator": ("Показник", "Indicator", "Indikator", "Indicateur", "指标", "Indicador", "Indicatore", "Indicador", "Wskaźnik", "Indicator", "Ukazatel", "Gösterge","指標", "지표", "संकेतक",),
    "col.leader": ("Лідер", "Leader", "Spitzenreiter", "Leader", "第一名", "Líder", "Leader", "Líder", "Lider", "Koploper", "Lídr", "Lider", "首位", "선두", "अग्रणी",),
    "col.gap": ("Різниця", "Gap", "Differenz", "Écart", "差距",  "Diferencia", "Differenza", "Diferença", "Różnica", "Verschil", "Rozdíl", "Fark", "差","차이", "अंतर",),

    "compare_pick": (
        "Країни для порівняння (до 3)", "Countries to compare (up to 3)",
        "Länder zum Vergleich (bis zu 3)", "Pays à comparer (jusqu'à 3)", "要比较的国家（最多3个）", "Países que comparar (hasta 3)", "Paesi da confrontare (fino a 3)", "Países a comparar (até 3)",
        "Kraje do porównania (do 3)", "Te vergelijken landen (maximaal 3)", "Země k porovnání (až 3)",
        "Karşılaştırılacak ülkeler (en fazla 3)", "比較する国（最大3か国）", "비교할 국가(최대 3개)",
        "तुलना के लिए देश (अधिकतम 3)",
    ),
    "compare_limit": (
        "Можна порівняти не більше 3 країн — показано перші три.",
        "You can compare up to 3 countries — showing the first three.",
        "Es lassen sich höchstens 3 Länder vergleichen – die ersten drei werden angezeigt.",
        "Vous pouvez comparer 3 pays au maximum — les trois premiers sont affichés.",
        "最多可比较3个国家，仅显示前三个。", "Se pueden comparar hasta 3 países; se muestran los tres primeros.",
        "Si possono confrontare al massimo 3 paesi: vengono mostrati i primi tre.",
        "Pode comparar até 3 países; são mostrados os três primeiros.",
        "Można porównać najwyżej 3 kraje — wyświetlono pierwsze trzy.",
        "Je kunt maximaal 3 landen vergelijken; de eerste drie worden getoond.",
        "Porovnat lze nejvýše 3 země — zobrazeny jsou první tři.",
        "En fazla 3 ülke karşılaştırılabilir; ilk üçü gösteriliyor.",
        "比較できるのは最大3か国です。最初の3か国を表示しています。",
        "최대 3개 국가까지 비교할 수 있어 처음 세 곳만 표시합니다.",
        "अधिकतम 3 देशों की तुलना की जा सकती है — पहले तीन दिखाए जा रहे हैं।",
    ),
    "choose": ("Оберіть…", "Choose…", "Auswählen…", "Choisir…", "请选择…", "Elija…", "Scegli…", "Escolha…", "Wybierz…", "Kies…", "Vyberte…", "Seçin…", "選択…", "선택…","चुनें…",),
    "why_not.title": (
        "Чому не X, а {winner}?", "Why {winner} and not X?", "Warum {winner} und nicht X?",
        "Pourquoi {winner} et pas X ?", "为什么是{winner}而不是X？",  "¿Por qué {winner} y no X?", "Perché {winner} e non X?", "Porque é que {winner} e não X?",
        "Dlaczego {winner}, a nie X?", "Waarom {winner} en niet X?", "Proč {winner} a ne X?",
        "Neden X değil de {winner}?", "なぜXではなく{winner}なのか？", "왜 X가 아니라 {winner}일까요?",
        "X की जगह {winner} क्यों?",
    ),
    "why_not.pick": ("Країна X", "Country X", "Land X", "Pays X", "国家X", "País X", "Paese X", "País X", "Kraj X", "Land X", "Země X", "Ülke X", "国X", "국가 X", "देश X",),
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
        "**{other}** obtiene {other_score} y **{winner}**, {winner_score}. Las barras a la derecha "
        "muestran dónde {other} pierde más puntos; las de la izquierda, dónde pierde menos.",
        "**{other}** ottiene {other_score}, **{winner}** {winner_score}. Le barre a destra mostrano "
        "dove {other} perde più punti, quelle a sinistra dove ne perde meno.",
        "**{other}** obtém {other_score} e **{winner}** {winner_score}. As barras à direita mostram "
        "onde {other} perde mais pontos; as da esquerda, onde perde menos.",
        "**{other}** ma {other_score} pkt, a **{winner}** {winner_score} pkt. Słupki w prawo pokazują, "
        "gdzie {other} traci więcej punktów, a w lewo — gdzie traci mniej.",
        "**{other}** scoort {other_score}, **{winner}** {winner_score}. Balken naar rechts tonen waar "
        "{other} meer punten verliest, balken naar links waar het er minder verliest.",
        "**{other}** získává {other_score} bodů, **{winner}** {winner_score}. Sloupce vpravo ukazují, "
        "kde {other} ztrácí více bodů, sloupce vlevo, kde jich ztrácí méně.",
        "**{other}** {other_score}, **{winner}** {winner_score} puan alıyor. Sağdaki çubuklar {other} "
        "ülkesinin daha fazla puan kaybettiği göstergeleri, soldakiler daha az kaybettiği göstergeleri "
        "gösterir.",
        "**{other}**は{other_score}点、**{winner}**は{winner_score}点です。右向きのバーは{other}の失点が"
        "多い指標、左向きのバーは失点が少ない指標を示します。",
        "**{other}**은(는) {other_score}점, **{winner}**은(는) {winner_score}점입니다. 오른쪽 막대는 "
        "{other}이(가) 더 많이 감점되는 지표, 왼쪽 막대는 덜 감점되는 지표입니다.",
        "**{other}** को {other_score} और **{winner}** को {winner_score} अंक मिले हैं। दाईं ओर की पट्टियाँ "
        "वे संकेतक दिखाती हैं जहाँ {other} के अधिक अंक कटते हैं, बाईं ओर की वे जहाँ कम कटते हैं।",
    ),

    "why_not.details": (
        "Детальніше за показниками", "Details by indicator", "Details nach Indikator", "Détail par indicateur",
        "按指标查看详情",
    ),

    "why_not.details": ("Дані таблицею", "Show as table", "Als Tabelle anzeigen", "Afficher le tableau", "以表格显示", "Mostrar como tabla", "Mostra come tabella", "Mostrar como tabela", "Pokaż jako tabelę","Als tabel tonen", "Zobrazit jako tabulku", "Tablo olarak göster", "表で表示", "표로 보기","तालिका के रूप में दिखाएँ",),

    "chart.points_lost": (
        "Втрачено балів до ідеалу", "Points lost vs. the ideal", "Verlorene Punkte zum Ideal",
        "Points perdus par rapport à l'idéal", "与理想相比失去的分数", "Puntos perdidos respecto al ideal", "Punti persi rispetto all'ideale",
        "Pontos perdidos em relação ao ideal", "Punkty utracone względem ideału",
        "Verloren punten ten opzichte van het ideaal", "Body ztracené oproti ideálu",
        "İdealine göre kaybedilen puanlar", "理想に対する失点", "이상 대비 감점",
        "आदर्श की तुलना में खोए अंक",
    ),
    "chart.gap_axis": (
        "Різниця втрачених балів: {other} − {winner}", "Difference in points lost: {other} − {winner}",
        "Differenz der verlorenen Punkte: {other} − {winner}", "Écart de points perdus : {other} − {winner}",
        "失分差：{other} − {winner}", "Diferencia de puntos perdidos: {other} − {winner}",
        "Differenza di punti persi: {other} − {winner}",
        "Diferença de pontos perdidos: {other} − {winner}",
        "Różnica utraconych punktów: {other} − {winner}",
        "Verschil in verloren punten: {other} − {winner}",
        "Rozdíl ztracených bodů: {other} − {winner}",
        "Kaybedilen puan farkı: {other} − {winner}",
        "失点の差：{other} − {winner}",
        "감점 차이: {other} − {winner}",
        "खोए अंकों का अंतर: {other} − {winner}",
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
    "chart.ideal": ("Ідеал", "Ideal", "Ideal", "Idéal", "理想", "Ideal", "Ideale", "Ideal", "Ideał", "Ideaal", "Ideál", "İdeal", "理想", "이상", "आदर्श",),
    # Categories
    "cat.safety": ("Безпека", "Safety", "Sicherheit", "Sécurité", "安全", "Seguridad", "Sicurezza", "Segurança", "Bezpieczeństwo", "Veiligheid", "Bezpečnost","Güvenlik", "安全", "안전", "सुरक्षा",),
    "cat.economy": ("Економіка", "Economy", "Wirtschaft", "Économie", "经济", "Economía", "Economia", "Economia", "Gospodarka", "Economie", "Ekonomika", "Ekonomi", "経済","경제", "अर्थव्यवस्था",),
    "cat.health": ("Здоров'я", "Health", "Gesundheit", "Santé", "健康", "Salud", "Salute", "Saúde", "Zdrowie", "Gezondheid", "Zdraví", "Sağlık", "健康", "건강","स्वास्थ्य",),
    "cat.environment": ("Довкілля", "Environment", "Umwelt", "Environnement", "环境", "Medio ambiente", "Ambiente", "Ambiente", "Środowisko", "Milieu", "Životní prostředí", "Çevre","環境", "환경", "पर्यावरण",),
    "cat.governance": ("Врядування", "Governance", "Regierungsführung", "Gouvernance", "治理", "Gobernanza", "Governance", "Governança", "Jakość rządzenia", "Bestuur","Správa věcí veřejných", "Yönetişim", "ガバナンス", "거버넌스", "शासन",),
    "cat.digital": ("Цифровізація", "Digital", "Digitalisierung", "Numérique", "数字化", "Digitalización", "Digitalizzazione", "Digitalização", "Cyfryzacja", "Digitalisering","Digitalizace", "Dijitalleşme", "デジタル化", "디지털화", "डिजिटलीकरण",),
    # Indicators (keyed by config.INDICATORS codes)
    "ind.WB_WDI_VC_IHR_PSRC_P5": (
        "Умисні вбивства на 100 тис.", "Intentional homicides per 100k",
        "Vorsätzliche Tötungen je 100.000", "Homicides volontaires pour 100 000", "每10万人故意杀人数", "Homicidios intencionales por 100 000 hab.", "Omicidi volontari ogni 100.000",
        "Homicídios dolosos por 100 000", "Zabójstwa umyślne na 100 tys.",
        "Opzettelijke doodslag per 100.000", "Úmyslné vraždy na 100 tis.",
        "100 binde kasıtlı cinayet", "人口10万人あたりの故意の殺人件数", "10만 명당 고의 살인 건수",
        "प्रति 1 लाख जानबूझकर की गई हत्याएँ",
    ),
    "ind.WB_WGI_PV_EST": (
        "Політична стабільність", "Political stability", "Politische Stabilität",
        "Stabilité politique", "政治稳定", "Estabilidad política", "Stabilità politica", "Estabilidade política", "Stabilność polityczna",
        "Politieke stabiliteit", "Politická stabilita", "Siyasi istikrar", "政治的安定", "정치적 안정",
        "राजनीतिक स्थिरता",
    ),
    "ind.WB_WDI_NY_GDP_PCAP_PP_CD": (
        "ВВП на душу (ПКС, $)", "GDP per capita (PPP, $)", "BIP pro Kopf (KKP, $)",
        "PIB par habitant (PPA, $)", "人均GDP（购买力平价，美元）", "PIB per cápita (PPA, $)", "PIL pro capite (PPA, $)", "PIB per capita (PPC, $)",
        "PKB na mieszkańca (PPP, $)", "Bbp per hoofd (PPP, $)", "HDP na obyvatele (PPP, $)",
        "Kişi başına GSYH (SGP, $)", "1人あたりGDP（購買力平価、ドル）", "1인당 GDP(PPP, 달러)",
        "प्रति व्यक्ति जीडीपी (पीपीपी, $)",
    ),
    "ind.WB_WDI_SL_UEM_TOTL_ZS": ("Безробіття, %", "Unemployment, %", "Arbeitslosigkeit, %", "Chômage, %", "失业率，%", "Desempleo, %", "Disoccupazione, %", "Desemprego, %", "Bezrobocie, %", "Werkloosheid, %","Nezaměstnanost, %", "İşsizlik, %", "失業率、%", "실업률, %", "बेरोज़गारी, %",),
    "ind.WB_WDI_FP_CPI_TOTL_ZG": ("Інфляція, %", "Inflation, %", "Inflation, %", "Inflation, %", "通货膨胀率，%", "Inflación, %", "Inflazione, %", "Inflação, %", "Inflacja, %", "Inflatie, %", "Inflace, %","Enflasyon, %", "インフレ率、%", "물가상승률, %", "मुद्रास्फीति, %",),
    "ind.WB_WDI_SP_DYN_LE00_IN": (
        "Очікувана тривалість життя", "Life expectancy", "Lebenserwartung", "Espérance de vie", "预期寿命", "Esperanza de vida", "Aspettativa di vita", "Esperança de vida", "Oczekiwana długość życia",
        "Levensverwachting", "Naděje dožití", "Yaşam beklentisi", "平均寿命", "기대수명",
        "जीवन प्रत्याशा",
    ),
    "ind.WB_WDI_SH_XPD_CHEX_PC_CD": (
        "Витрати на охорону здоров'я на душу, $", "Health spending per capita, $",
        "Gesundheitsausgaben pro Kopf, $", "Dépenses de santé par habitant, $", "人均卫生支出，美元", "Gasto sanitario per cápita, $", "Spesa sanitaria pro capite, $",
        "Despesa em saúde per capita, $", "Wydatki na zdrowie na mieszkańca, $",
        "Zorguitgaven per hoofd, $", "Výdaje na zdravotnictví na obyvatele, $",
        "Kişi başına sağlık harcaması, $", "1人あたり医療支出、ドル", "1인당 보건 지출, 달러",
        "प्रति व्यक्ति स्वास्थ्य व्यय, $",
    ),
    "ind.WB_WDI_EN_ATM_PM25_MC_M3": (
        "Забруднення повітря PM2.5", "Air pollution (PM2.5)", "Luftverschmutzung (PM2,5)",
        "Pollution de l'air (PM2,5)", "空气污染（PM2.5）", "Contaminación del aire (PM2,5)", "Inquinamento atmosferico (PM2,5)", "Poluição do ar (PM2,5)",
        "Zanieczyszczenie powietrza (PM2,5)", "Luchtvervuiling (PM2,5)", "Znečištění ovzduší (PM2,5)",
        "Hava kirliliği (PM2,5)", "大気汚染（PM2.5）", "대기오염(PM2.5)", "वायु प्रदूषण (PM2.5)",
    ),
    "ind.WB_WGI_CC_EST": (
        "Контроль корупції", "Control of corruption", "Korruptionskontrolle",
        "Maîtrise de la corruption", "腐败控制", "Control de la corrupción", "Controllo della corruzione", "Controlo da corrupção",
        "Kontrola korupcji", "Corruptiebestrijding", "Kontrola korupce", "Yolsuzluğun kontrolü",
        "汚職の抑制", "부패 통제", "भ्रष्टाचार नियंत्रण",
    ),
    "ind.WB_WDI_IT_NET_USER_ZS": (
        "Користувачі інтернету, %", "Internet users, %", "Internetnutzer, %", "Internautes, %", "互联网用户，%", "Usuarios de internet, %", "Utenti internet, %", "Utilizadores de internet, %",
        "Użytkownicy internetu, %", "Internetgebruikers, %", "Uživatelé internetu, %",
        "İnternet kullanıcıları, %", "インターネット利用者、%", "인터넷 이용자, %",
        "इंटरनेट उपयोगकर्ता, %",
    ),
    # Presets (keyed by their id in presets.py)
    "preset.student": ("Студент", "Student", "Student", "Étudiant", "学生", "Estudiante", "Studente", "Estudante", "Student", "Student", "Student", "Öğrenci", "学生","학생", "छात्र",),
    "preset.remote": (
        "Віддалений працівник", "Remote worker", "Remote-Beschäftigte", "Télétravailleur", "远程工作者", "Trabajador remoto", "Lavoratore da remoto", "Trabalhador remoto", "Pracownik zdalny",
        "Thuiswerker", "Vzdálený pracovník", "Uzaktan çalışan", "リモートワーカー", "원격 근무자",
        "रिमोट कर्मचारी",
    ),
    "preset.family": (
        "Сім'я з дітьми", "Family with children", "Familie mit Kindern", "Famille avec enfants",
        "有孩子的家庭", "Familia con hijos", "Famiglia con figli", "Família com filhos", "Rodzina z dziećmi",
        "Gezin met kinderen", "Rodina s dětmi", "Çocuklu aile", "子どものいる家族", "자녀가 있는 가족",
        "बच्चों वाला परिवार",
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
        "Asie de l'Est et Pacifique", "东亚与太平洋", "Asia oriental y el Pacífico", "Asia orientale e Pacifico", "Ásia Oriental e Pacífico",
        "Azja Wschodnia i Pacyfik", "Oost-Azië en Pacific", "Východní Asie a Tichomoří",
        "Doğu Asya ve Pasifik", "東アジア・太平洋", "동아시아·태평양", "पूर्वी एशिया और प्रशांत",
    ),
    "region.Europe & Central Asia": (
        "Європа і Центральна Азія", "Europe & Central Asia", "Europa und Zentralasien",
        "Europe et Asie centrale", "欧洲与中亚", "Europa y Asia central", "Europa e Asia centrale", "Europa e Ásia Central",
        "Europa i Azja Środkowa", "Europa en Centraal-Azië", "Evropa a Střední Asie",
        "Avrupa ve Orta Asya", "欧州・中央アジア", "유럽·중앙아시아", "यूरोप और मध्य एशिया",
    ),
    "region.Latin America & Caribbean": (
        "Латинська Америка і Карибський басейн", "Latin America & Caribbean",
        "Lateinamerika und Karibik", "Amérique latine et Caraïbes", "拉丁美洲和加勒比", "América Latina y el Caribe", "America Latina e Caraibi", "América Latina e Caribe",
        "Ameryka Łacińska i Karaiby", "Latijns-Amerika en het Caribisch gebied",
        "Latinská Amerika a Karibik", "Latin Amerika ve Karayipler", "ラテンアメリカ・カリブ",
        "라틴 아메리카·카리브", "लैटिन अमेरिका और कैरिबियन",
    ),
    "region.Middle East, North Africa, Afghanistan & Pakistan": (
        "Близький Схід, Північна Африка, Афганістан і Пакистан",
        "Middle East, North Africa, Afghanistan & Pakistan",
        "Naher Osten, Nordafrika, Afghanistan und Pakistan",
        "Moyen-Orient, Afrique du Nord, Afghanistan et Pakistan", "中东、北非、阿富汗和巴基斯坦", "Oriente Medio, norte de África, Afganistán y Pakistán",
        "Medio Oriente, Nord Africa, Afghanistan e Pakistan",
        "Médio Oriente, Norte de África, Afeganistão e Paquistão",
        "Bliski Wschód, Afryka Północna, Afganistan i Pakistan",
        "Midden-Oosten, Noord-Afrika, Afghanistan en Pakistan",
        "Blízký východ, severní Afrika, Afghánistán a Pákistán",
        "Orta Doğu, Kuzey Afrika, Afganistan ve Pakistan",
        "中東・北アフリカ・アフガニスタン・パキスタン",
        "중동·북아프리카·아프가니스탄·파키스탄",
        "मध्य पूर्व, उत्तरी अफ्रीका, अफ़ग़ानिस्तान और पाकिस्तान",
    ),
    "region.Middle East & North Africa": (
        "Близький Схід і Північна Африка", "Middle East & North Africa", "Naher Osten und Nordafrika",
        "Moyen-Orient et Afrique du Nord", "中东和北非", "Oriente Medio y norte de África", "Medio Oriente e Nord Africa",
        "Médio Oriente e Norte de África", "Bliski Wschód i Afryka Północna",
        "Midden-Oosten en Noord-Afrika", "Blízký východ a severní Afrika",
        "Orta Doğu ve Kuzey Afrika", "中東・北アフリカ", "중동·북아프리카",
        "मध्य पूर्व और उत्तरी अफ्रीका",
    ),
    "region.North America": ("Північна Америка", "North America", "Nordamerika", "Amérique du Nord", "北美", "América del Norte", "Nord America", "América do Norte", "Ameryka Północna", "Noord-Amerika","Severní Amerika", "Kuzey Amerika", "北米", "북미", "उत्तरी अमेरिका",),
    "region.South Asia": ("Південна Азія", "South Asia", "Südasien", "Asie du Sud", "南亚", "Asia meridional", "Asia meridionale", "Sul da Ásia", "Azja Południowa", "Zuid-Azië","Jižní Asie", "Güney Asya", "南アジア", "남아시아", "दक्षिण एशिया",),
    "region.Sub-Saharan Africa": (
        "Африка на південь від Сахари", "Sub-Saharan Africa", "Subsahara-Afrika",
        "Afrique subsaharienne", "撒哈拉以南非洲", "África subsahariana", "Africa subsahariana", "África Subsariana", "Afryka Subsaharyjska",
        "Sub-Saharaans Afrika", "Subsaharská Afrika", "Sahra Altı Afrika", "サハラ以南アフリカ",
        "사하라 이남 아프리카", "उप-सहारा अफ्रीका",
    ),
    # Economies without an ISO 3166 / CLDR entry
    "country.CHI": ("Нормандські острови", "Channel Islands", "Kanalinseln", "Îles Anglo-Normandes", "海峡群岛", "Islas del Canal", "Isole del Canale", "Ilhas do Canal", "Wyspy Normandzkie", "Kanaaleilanden","Normanské ostrovy", "Manş Adaları", "チャンネル諸島", "채널 제도", "चैनल द्वीप समूह",),
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
