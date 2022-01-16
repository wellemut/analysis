from helpers.extractors import BaseExtractor, FacebookExtractor


def test_it_is_an_extractor():
    assert issubclass(FacebookExtractor, BaseExtractor)


def test_it_extracts_valid_handles():
    links = {
        "https://facebook.com/UNSDSN": "unsdsn",
        "https://facebook.com/UNSDSN/": "unsdsn",
        "http://www.facebook.com/UNSDSN": "unsdsn",
        "https://www.facebook.com/SDSNMX/?ref=br_rs": "sdsnmx",
        "https://www.facebook.com/BCProvincialGovernment/videos/761567411297253/?__so__=channel_tab&__rv__=playlists_card": "bcprovincialgovernment",
        "https://de-de.facebook.com/PIKPotsdam": "pikpotsdam",
        "https://www.facebook.com/100115905140667/posts/395624258923162": "100115905140667",
        "https://www.facebook.com/DIE.Bonn": "die.bonn",
        "https://www.facebook.com/Georgia-Campus-Sustainability-Network-148788518526034/": "georgia-campus-sustainability-network-148788518526034",
        "https://www.facebook.com/IISDnews?ref=ts&fref=ts": "iisdnews",
        "https://www.facebook.com/R%C3%A9seau-des-Anciens-J%C3%A9cistes-Rajas-109361183850951/": "r%c3%a9seau-des-anciens-j%c3%a9cistes-rajas-109361183850951",
        "https://www.facebook.com/202099226601764_2366366110175054": "202099226601764",
        "https://www.facebook.com/BerlKönig-277118882878908/": "berlkönig-277118882878908",
        "http://www.facebook.com/onvista#footer": "onvista",
        "https://business.facebook.com/zfgroup.deutschland/?business_id=877856885590278": "zfgroup.deutschland",
        "https://business.facebook.com/DPD-Schweiz-2157314227618201/?business_id=472189330192746&modal=admin_todo_tour": "dpd-schweiz-2157314227618201",
        "https://facebook.com//stadtbibliothek.emsdetten": "stadtbibliothek.emsdetten",
    }
    for url, handle in links.items():
        assert (url, FacebookExtractor.extract(url)) == (url, handle)


def test_it_extracts_valid_handles_from_pages_link():
    links = {
        "https://www.facebook.com/pages/Climate-Security-Link/256148737731271": "256148737731271",
        "https://www.facebook.com/pages/Churches-in-Action-for-Peace-and-Development-CAPAD/240823892635570": "240823892635570",
        "https://www.facebook.com/pages/category/Organization/UN-SDSN-Mediterranean-943912399003930/": "un-sdsn-mediterranean-943912399003930",
        "https://www.facebook.com/pages/World-Bank-Albania/814943071852288?fref=ts": "814943071852288",
        "https://www.facebook.com/pg/CongressWomenKR/about/": "congresswomenkr",
        "http://www.facebook.com/#!/pages/Deutsche-Welle-Kiswahili/144393622272640": "144393622272640",
        "http://www.facebook.com/pages/Berlin/Zentrum-Technik-und-Gesellschaft/94157038294": "94157038294",
    }
    for url, handle in links.items():
        assert (url, FacebookExtractor.extract(url)) == (url, handle)


def test_it_ignores_developers_subdomain():
    links = [
        "https://developers.facebook.com/docs/plugins/",
        "http://developers.facebook.com/plugins",
        "http://developers.facebook.com/mypageinvalid",
    ]
    for url in links:
        assert (url, FacebookExtractor.extract(url)) == (url, None)


def test_it_ignores_links_without_valid_handle():
    links = [
        "https://www.facebook.com/",
        "https://www.facebook.com/#!",
        "https://www.facebook.com/share.php?u=https://www.icanw.org/emergingtechnologies",
        "http://www.facebook.com/sharer.php?u=https://cleancooking.org/news/senators-introduce-bipartisan-bill-to-support-clean-cooking/",
        "https://www.facebook.com/sharer/sharer.php?u=https%3A%2F%2Ffutureearth.org%2Fevent%2Fsri2022%2F",
        "https://l.facebook.com/l.php?u=https%3A%2F%2Fglobalchallenges.org%2Fbeyond-babel-participatory-platforms-and-cross-border-narratives%2F&h=AT302TwrcSJ0l5JusA6oQ2GxgMEuA0XwPErWB6At6985XoAmAgGw45I-efNAV6Bufyzoy1VM9VZgWAVkehEIb5yXz6dA4rkWhw3cN201r_1gWyOPJJWBhEcMz26AY3cdFMi-GKALjUquge91Bu_f&s=1",
        "http://www.facebook.com/dialog/send?app_id=244677186975162&link=https%3A%2F%2Fwww.transparency.org%2Fen%2Fblog%2Fadjust-clarify-simplify-how-integrity-pacts-promote-better-value-for-money%3Futm_source%3Dmessenger%26utm_medium%3Dsocial%26utm_campaign%3Dshare-button&redirect_uri=https://www.transparency.org/en/blog/adjust-clarify-simplify-how-integrity-pacts-promote-better-value-for-money%3Futm_source%3Dmessenger%26utm_medium%3Dsocial%26utm_campaign%3Dshare-button",
        # Internal
        "https://en-gb.facebook.com/policy.php",
        "https://facebook.com/about/privacy/",
        "https://www.facebook.com/legal/terms/update",
        "https://www.facebook.com/policies/cookies/",
        "https://www.facebook.com/policy",
        "https://www.facebook.com/login",
        "https://www.facebook.com/login.php?next=https%3A%2F%2Fwww.facebook.com%2Fads%2Fpreferences%2F%3Fentry_product%3Dad_settings_screen"
        "https://www.facebook.com/settings",
        "https://www.facebook.com/help",
        "https://www.facebook.com/hashtag/solarenergie",
        "https://www.facebook.com/ads/preferences/?entry_product=ad_settings_screen",
        "https://www.facebook.com/communitystandards",
        "https://www.facebook.com/plugins/like.php?href=https%3A%2F%2Fwww.private-banking-magazin.de%2Fanlegern-koennten-unruhige-zeiten-bevorstehen%2F",
        "https://www.facebook.com/terms.php",
        # Business
        "https://www.facebook.com/business/a/online-sales/custom-audiences-website",
        # Events
        "https://fb.me/e/2kYpOWcJH",
        "https://www.facebook.com/events/416247446865669",
        # Photos/Videos
        "https://www.facebook.com/photo.php?fbid=10157185531569314&set=a.10150146525164314&type=3&eid=ARDzYLW5LZuYoGa0fUYj22zKqVFExZnj53HGSzQXu8sTCZaknDYXqB89p0rwucF5srCh50wlaJHXo5jb",
        "https://www.facebook.com/watch/?v=222993302362567&t=10",
        # Funding/donations
        "https://www.facebook.com/donate/1102848833822116/10158603955417215/",
        "https://www.facebook.com/fund/TransparencyInternational/",
        # Other
        "https://www.facebook.com/groups",
        "https://www.facebook.com/permalink.php?story_fbid=947623255310128&id=145391055533356",
        "https://www.facebook.com/profile.php?id=100006608898044",
    ]
    for url in links:
        assert (url, FacebookExtractor.extract(url)) == (url, None)
