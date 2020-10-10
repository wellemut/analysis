# Analyze website HTML one after the other
from bs4 import BeautifulSoup
import re
from database.get_next_url_to_analyze import get_next_url_to_analyze
from database.add_matches import add_matches

KEYWORDS = {
    "sdgs": "SDGs? | Sustainable Development Goals? | Nachhaltigkeitsziele? | Ziele für Nachhaltige Entwicklung",
    "sdg1": "Armut | ärm* | Sozialsystem | Sozialschutzsystem | Grundsicherung | Mikrofinanz* | Basisschutz | arm* | poverty | poor | social protection system | microfinanc* | basic income | basic provision | basic social security |",
    "sdg2": "Hunger | Nahrung* | nachhaltige Landwirtschaft | Landwirtschaft | Agrar* | Saat* | *Ernährung | essen* | Bauer* | Kleinbauer | Übergewicht* | Fehlernähr* | Adipositas | Adipös | Fettleibigkeit | Obesitas | food | algricult* | hunger | farm* | *nutrition | sustainable farm* | pastoralist | fisher | seed | cultivat* | domesticate | livestock | obesity | overweight | obese | eat* |",
    "sdg3": "Gesund* | Wohlergehen | Müttersterb* | Kindersterb* | Epidem* | Krankheit* | Frühsterblich* | Impf* | Lebendgeburt* | Neugeb* | Arznei* | Medikament* | Medizin* | Todes* | Aids* | Tuberkulose* | Malaria* | Behandl* | Sucht* | Drogen* | Verletz* | Lebenserwartung* | Sterblichkeit | Unfalltot* |sex* | Hygiene | sauber* | Ärzt* | Arzt | Doktor | Patient | Praxis  | Betreuung | behind*| Therapie | Wohlbefinden | Lebensqualität | Pflege |  health | diseas* | medicin* | mortal* | birth* | death* | vaccine* | well-being |newborn | neonatal mortality | epidemics | aids | tuberculosis | malaria | narcotic* | drug* | injur* | accident | reproductive | illness* | hygien* | life expectancy | Doctor | Therapy | pharma* | Care | Handicap | disab* |",
    "sdg4": "*Bildung | *bilden | Qualifi* | *schul* | Analphabet* | Schüler* | lernen | Unterricht* | student | Lehr* | educat* | vocation* | training | school | literacy | illiterate | pupil | teach* | learn |",
    "sdg5": "Geschlechterg* | Chanceng* | Selbstbestimm* | Diskrimi* | Menschenhandel | Verhütung* | Gleichstellung* | Mädchen | Diversit*| Kinderheirat | Zwangsheirat | Zwangsehe | Genitalverstü* | Beschneidung | Gender Pay Gap | Gender Wage Gap | equality | gender | empowerment | self-determine* | discriminat* | trafficking | forced marriage | genital mutilation | circumcision |  child marriage | Gender Pay Gap | Gender Wage Gap | emancipat* | Emanz*| Frau* | Woman | Women | Girls |",
    "sdg6": "Sauberes Wasser | Sanitär* | Wasserknapp* | Wassernutz* | Trinkwasser | Notdurftverricht* | Wasserqualität | Abwasser | Wasserressourcen | Grundwasser | Frischwasser | WC | clean water | water usage | water scarcity | water quality | water reuse | water recycling | water resources | sanitation | wastewater | open defecation | freshwater | water-related | wetland | aquifer | water efficiency | water harvesting | desalinat* | toilette | toilet | ",
    "sdg7": "Energie* | Erneuerbare Energie | Energiewende | Brennstoff* | Strom* | Windturbine | Photovoltaik* | Solar* | Biogas* | PV*Anlage | Batterie* | clean energy | green energy | modern energy | renewable energy | sustainable energy | photovoltaic | wind turbine | solar | biogas | energy efficiency | clean fossil-fuel | energy infrastructure | energy technology | energy storage | power supply | energy grid | power grid |",
    "sdg8": "Kinderarbeit | Vollbeschäftigung | Wirtschaftswachstum | Bruttoinlandsprodukt* | Arbeitspl* | menschenwürdig* | nachhaltiges Wachstum | Zwangsarbeit | Sklaverei | Menschenhandel | Kindersoldat* | Arbeitsrecht* | Wanderarbeit* | prekär* Beschäftig* | nachhaltiger Tourismus | Arbeitslos* |Arbeitsbeschaffung* | *employ* | labor | labour | economic growth | gross domestic product | economic productivity | job creation | sustainable growth | job | decent work | slavery | child soldiers | sustainable tourism | working environment | worker | ",
    "sdg9": "Infrastruktur* | Industrialisierung | Technologieentwicklung | Technologieförderung | Forschung* | Internetzugang | verkehr | industrie 4.0 | Fahr* | Mobilität | Logistik* | Industrie 4 | künstliche Intelligenz | maschinelles lernen | infrastructure | industrialisation | industrialization | research | technology transfer | technology support | technology development | access to internet | internet access | development spending | R&D | smart | traffic | transport | digital* | IoT | internet of things | industry 4.0 | automat* | augmented reality | virtual reality | driv* | vehicle* | Mobility | logistic* | industry 4 | machine learning | artificial intelligence | ",
    "sdg10": "Ungleichheit* | Einkommenswachstum | Selbstbestimm* | Inklusion | Geschlechterg* | Chanceng* | Diskrimi* | Lohnungleichheit* | Arm und Reich | Lohnunterschied* | Entwicklungsl* | Migration* | Flüchtling | Flucht | Teilhabe | Partizipation | barrierefrei* | Behinder* | Diversit* |flücht* | Rollstuhl | inequalit* | unequal* | income growth | inclusion | discriminit* | equality | poor and rich | developing countr* | migration | inclusive | refugee | Disabilit* | Wheelchair |",
    "sdg11": "Nachhaltige Städte | Nachhaltige Stadt| Nachhaltige Gemeind* | Gemeinde* | Wohnraum | Slum* | *Verkehr* | öffentlicher Nahverkehr | ÖPNV | Verstädterung | Siedlung* | Weltkulturerbe | Weltnaturerbe | Gentrifizier* | komunal* | Naturkatastrophen | nachhaltiges Bauen | nachhaltiges Baumaterial* | nachhaltige Baumaterial* | stadt | städte |  kommun* | städti* | Elektro* | Mobilität | Logistik* | sustainable cit* | sustainable communit* | public transport | traffic | settlement | slum | sustainable transport | affordable transport | safe transport |  accessible transport | housing | urbanization | urbanization | public space | green space | safe space | disaster | sustainable building | building sustainable | construction |  cultural heritage | natural heritage | city | cities | communit* | electr* | Mobility | logistic* |",
    "sdg12": "Konsum* | nachhaltige Produktion | Produktionsmuster | Ressourceneinsatz | Ressourcennutz* | Ressourcenproduk* | Abfall* | Abfälle | Nahrungsmittelverschwendung | Nahrungsmittelverluste | Nachernteverluste | Kreislaufwirtschaft | Wiederverwendung | Wiederverwertung | Elektroschrott | nachhaltiger Einkauf | nachhaltiger Tourismus | nachhaltig* | umweltfreund* | Recycling | Recyc* | E*waste | sustainable production | sustainable consumption | consumption | resource efficiency | food waste | food loss* |  post-harvest loss* | circular economy | circular business | recycling | waste | reuse | sustainable procurement | sustainable tourism | e*waste | fair trade | sustain* | eco-friendly | environmentally friendly | share | sharing | organic | bio* | ecological |",
    "sdg13": "Klimawandel* | Klimaschutz* | CO2 | Treibhausgas* | klimabedingt | klimafolge* | Klimaanpassung* | Klimaauswirk* | Emission* | climate change | climate action | climate mitigation | climate adaptation | CO2 | greenhouse gas | climate related | Emission |",
    "sdg14": "Ozean* | Meeresressource* | Fischerei* | Überfisch* | Küstenökosystem* | Fischbestand | Fischbestände | Aquakultur* | Meerestechnolog* | Kleinfischer | marine | ocean* | fishing | fisheries | coastal | overfishing | aquaculture | fish | ",
    "sdg15": "Bodendegradation | Landökosysteme | Desertifikation | Wald* | Artenvielfalt | Wälder | Wüstenbild* | *aufforst* | Wilderei | Entwald* | Biodiversität |ökologische Vielfalt | biologische Vielfalt | bedrohte Arten | Aussterben | Neobiota | invasive Arten | invasive* gebietsfremde* Art*| Ökosystemdiversität  | Flächenversiegel* | Erosion | biodiversity | forest* | desertificat* | poach* | reforest* | terrestrial ecosystem* | renaturation* | natural habitat* | extinction | threatened species | wildlife | invasive species | alien species | eradicat* |  non-indigenous species | impervious surface |",
    "sdg16": "Friede* | Gewalt* | Justiz* | Krimin* | Rechtsstart* | Waffen* | Korruption | Bestechung | Kleptokrat* | Völkerrecht* | Menschenrecht* | Mord* | Verbrech* | leistungsfähige Institutionen | rechenschaftspflichtige Institutionen | inklusive Institutionen | Sicher* | justice | peace | violence | war | effective institution* | accountable institution* | inclusive institution* | crime | criminal | | judici* | torture | rule of law | weapon | illicit | corrupt* | brib* | transparent institutions | human rights | international law | kleptocracy | participat* | Secur* |",
    "sdg17": "Entwicklungshilfe* | Entwicklungszusammenarbeit* | Nord-Süd-Zusammenarbeit | Süd-Süd-Zusammenarbeit | Dreieckskooperation* | Leapfrog* | Technologietransf* | Kapazitätsaufbau* | Capacity Building | fairer Welthandel | gerechter Welthandel | Handelsbarriere* | Protektionismus | development aid | development assistance | development cooperation | foreign aid | capacity building | north-south | ODA | official development assistance | least developed countr* | south-south | triangular cooperation | technology transfer | technology facilitation | leapfrog* | fair trade | trade barriers | "
}

# Prepare search regexes
regex_patterns = {}
for goal, needle in KEYWORDS.items():
    # Generate list of search terms
    search_terms = [term.strip() for term in needle.split("|")]

    # Remove empty strings
    search_terms = list(filter(None, search_terms))

    # Convert * character into wildcard match
    search_terms = [term.replace("*", r"\w*?") for term in search_terms]

    # Search for keyword
    pattern = re.compile(r'\b(%s)\b' % "|".join(search_terms), flags=re.IGNORECASE | re.DOTALL)
    regex_patterns[goal] = pattern

# Analyze each HTML snippet in database
while url_object := get_next_url_to_analyze():
    url = url_object["url"]
    html = url_object["html"]
    print("Searching for keywords in scraped HTML for", url, end=" ... ", flush=True)

    # Convert HTML to text
    soup = BeautifulSoup(html, 'html.parser')
    text = soup.get_text().strip()

    # Search for keywords in string
    matches = {}
    for goal, pattern in regex_patterns.items():
        for match in pattern.finditer(text):
            matches[goal] = matches.get(goal, [])
            matches[goal].append(match.group())

    # Write matches to database
    add_matches(url=url, matches=matches, word_count=len(text.split()))

    print("Done")
    print(matches)
