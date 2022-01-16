from helpers.extractors import BaseExtractor, TwitterExtractor


def test_it_is_an_extractor():
    assert issubclass(TwitterExtractor, BaseExtractor)


def test_it_extracts_valid_handles():
    links = {
        "http://twitter.com/#!/ArcheNova": "archenova",
        "http://twitter.com/@JadDaley": "jaddaley",
        "http://twitter.com/FSC_IC/status/1371492016350187522?s=20": "fsc_ic",
        "https://twitter.com/2net__________": "2net__________",
        "https://twitter.com/AlexNHalliday?ref_src=twsrc%5Etfw": "alexnhalliday",
        "https://twitter.com//impact_lab": "impact_lab",
        "https://mobile.twitter.com/simonestrey?lang=en": "simonestrey",
        "https://twitter.com/en": "en",
        "https://twitter.com/de": "de",
        "https://twitter.com/RachelPotter8/timelines/1181524816463040512?ref_src=twsrc%5Etfw": "rachelpotter8",
        "https://twitter.com/GrueneBundestag/lists/mdb19": "gruenebundestag",
    }
    for url, handle in links.items():
        assert (url, TwitterExtractor.extract(url)) == (url, handle)


def test_it_extracts_handles_from_intents():
    links = {
        "https://twitter.com/intent/tweet?related=greenpeace&text=2020%3A%20The%20year%20that%20was, via @greenpeace&url=https%3A%2F%2Fwww.greenpeace.org%2Finternational%2Fstory%2F46003%2F2020-greenpeace-climate-change%2F%3Futm_medium%3Dshare%26utm_content%3Dpostid-46003%26utm_source%3Dtwitter": "greenpeace",
        "https://twitter.com/intent/tweet?url=https://www.globalgovernance.eu/press/publications/ggi-briefing-paper-civil-society-reforms-in-uzbekistan-more-than-government-chicanery/&text=GGI+Briefing+Paper%3A+Civil+Society+reforms+in+Uzbekistan%3A+More+than+government+chicanery%3F&via=GlobalGovInst": "globalgovinst",
        "https://twitter.com/intent/tweet?related=twitter%3ATwitter%20News,twitterapi%3ATwitter%20API%20News": "twitter",
        "https://twitter.com/share?contenturl=iiasa.ac.at%2Fweb%2Fhome%2Fabout%2Falumni%2FIIASA_Network.html&text=IIASA+Network+and+Alumni%3Cbr%3E&via=IIASAVienna": "iiasavienna",
        "https://twitter.com/intent/tweet/?url=https://www.bosch-stiftung.de/de/aktuelles/alle-meldungen&text=Lesenswertes von der @BoschStiftung": "boschstiftung",
        "https://twitter.com/intent/tweet?text=%40IMMOVATION_AG%20%23MIPIM%20verschoben%20doch%20unsere%20Bewerbungsphase%20findet%20statt.%20Schaut%20mal%20hier%3A%20https%3A%2F%2Ft.co%2FLI3O4iBoSa%20Jetzt%20noch%20bis%20zum%2031.%20Mai%20die%20Gelegenheit%20nutzen%20und%20bewerben!%20%23Call4Innovation%20%23PropTech%20%23Startup": "immovation_ag",
        "http://twitter.com/intent/follow?source=followbutton&variant=1.0&screen_name=engvillage": "engvillage",
        "https://twitter.com/intent/retweet?tweet_id=1351099510685003776&related=NeueWirtschaft": "neuewirtschaft",
    }
    for url, handle in links.items():
        assert (url, TwitterExtractor.extract(url)) == (url, handle)


def test_it_ignores_subdomains_other_than_www():
    links = [
        "https://about.twitter.com/content/dam/about-twitter/en/company/global-impact-2020.pdf",
        "https://business.twitter.com/en/help/ads-policies/introduction-to-twitter-ads/twitter-ads-policies.html",
        "https://help.twitter.com/en/rules-and-policies/twitter-cookies#",
        "https://dev.twitter.com/web/overview",
        "https://developer.twitter.com/en/docs/twitter-for-websites/overview",
        "https://gdpr.twitter.com/en/controller-to-controller-transfers.html",
        "https://legal.twitter.com/imprint",
        "https://support.twitter.com/articles/105576#",
    ]
    for url in links:
        assert (url, TwitterExtractor.extract(url)) == (url, None)


def test_it_ignores_links_without_valid_handle():
    links = [
        "http://twitter.com",
        "http://twitter.com/#",
        "http://twitter.com/#/",
        "http://twitter.com/#!",
        "http://twitter.com/#!/",
        # Reserved
        "https://twitter.com/i/status/1420869606072365067",
        "https://twitter.com/i/web/status/1479570041817419783",
        "https://twitter.com/i/lists/122101272",
        "https://twitter.com/i/moments/1328612654592782336?ref_src=twsrc%5Etfw",
        # Search, home, feed,. ...
        "http://twitter.com/home/?status=Berlin's districts and their local way towards circularity - https://circular.berlin/berlins-districts-and-their-local-way-towards-circularity/",
        "http://twitter.com/#!/search?q=%23UpdateDeutschland",
        "https://twitter.com/hashtag/climatechange?src=hashtag_click"
        "https://twitter.com/intent/like?tweet_id=1458532413345312774",
        "https://twitter.com/share",
        "https://twitter.com/share?url=https%3A%2F%2Fwww.wbgu.de%2Fen%2Fpublications%2Fpublication%2Fpp10-2019"
        # Technically valid, but more difficult to link to, so we ignore for now
        "http://twitter.com/intent/user?user_id=1072187272815149057",
        # Invalid handle (period in username)
        "https://twitter.com/intent/tweet?via=social_handles.twitter&text=90%20manufacturing%20sites%20are%20scaling%20innovations%20on%20our%20learning%20network&url=https%3A%2F%2Fwww.weforum.org%2Four-impact%2Fadvanced-manufacturing-factories-light-the-way-as-learning-beacons%2F",
        # Internal
        "http://twitter.com/account/settings",
        "https://twitter.com/settings/security",
        "https://twitter.com/en/privacy",
        "https://twitter.com/privacy",
    ]
    for url in links:
        assert (url, TwitterExtractor.extract(url)) == (url, None)
