import requests
from bs4 import BeautifulSoup
import logging

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

def check_sql_injection(soup):
    sql_patterns = ["SELECT", "UNION", "INSERT", "UPDATE", "DELETE", "DROP"]
    if any(pattern in soup.text.upper() for pattern in sql_patterns):
        return "Olası SQL Enjeksiyonu"
    return None

def check_xss(soup):
    if "<script>" in soup.prettify().lower():
        return "Olası XSS (Cross-Site Scripting) Açığı"
    return None

def check_csrf_protection(soup):
    forms = soup.find_all('form')
    for form in forms:
        if 'csrf' not in form.prettify().lower():
            return "CSRF Koruma Eksikliği"
    return None

def check_clickjacking_protection(response):
    if "X-Frame-Options" not in response.headers:
        return "Clickjacking Koruma Eksikliği (X-Frame-Options Başlığı)"
    return None

def check_security_headers(response):
    missing_headers = []
    security_headers = {
        "Content-Security-Policy": "İçerik Güvenlik Politikası (CSP)",
        "Strict-Transport-Security": "Katı Taşıma Güvenliği (HSTS)",
        "X-Content-Type-Options": "İçerik Tipi Seçenekleri (XCTO)",
        "X-XSS-Protection": "XSS Koruması (XXSSP)",
        "Referrer-Policy": "Yönlendirme Politikası",
        "Permissions-Policy": "İzinler Politikası"
    }
    for header, name in security_headers.items():
        if (response.headers.get(header) is None or 
            response.headers.get(header).strip() == ""):
            missing_headers.append(f"{name} Başlığı Eksik ({header})")
    return missing_headers

def check_https_usage(url):
    if not url.lower().startswith('https'):
        return "URL HTTPS kullanmıyor"
    return None

def check_server_information(response):
    if "Server" in response.headers:
        return f"Sunucu Bilgisi: {response.headers['Server']}"
    return None

def check_cookie_security(response):
    if "Set-Cookie" in response.headers:
        cookies = response.headers.getlist('Set-Cookie')
        insecure_cookies = [cookie for cookie in cookies if "Secure" not in cookie or "HttpOnly" not in cookie]
        if insecure_cookies:
            return "Güvensiz Çerezler Tespit Edildi (Secure ve HttpOnly bayrakları eksik)"
    return None

def url_scanner(url):
    vulnerabilities = []

    https_vuln = check_https_usage(url)
    if https_vuln:
        vulnerabilities.append(https_vuln)

    try:
        response = requests.get(url)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        logging.error(f"{url} adresine erişimde hata: {e}")
        return

    soup = BeautifulSoup(response.content, 'html.parser')

    for check in [check_sql_injection, check_xss, check_csrf_protection, check_clickjacking_protection]:
        result = check(soup if check != check_clickjacking_protection else response)
        if result:
            vulnerabilities.append(result)

    vulnerabilities.extend(check_security_headers(response))

    for check in [check_server_information, check_cookie_security]:
        result = check(response)
        if result:
            vulnerabilities.append(result)

    if vulnerabilities:
        logging.info(f"{url} adresinde bulunan güvenlik açıkları:")
        for vulnerability in vulnerabilities:
            logging.info(vulnerability)
    else:
        logging.info(f"{url} güvenli görünüyor")

def main():
    text_art = """
             \033[31m:::!~!!!!!:.
                  .xUHWH!! !!?M88WHX:.
                .X*#M@$!!  !X!M$$$$$$WWx:.
               :!!!!!!?H! :!$!$$$$$$$$$$8X:
              !!~  ~:~!! :~!$!#$$$$$$$$$$8X:
             :!~::!H!<   ~.U$X!?R$$$$$$$$MM!
             ~!~!!!!~~ .:XW$$$U!!?$$$$$$RMM!
               !:~~~ .:!M"T#$$$$WX??#MRRMMM!
               ~?WuxiW*`   `"#$$$$8!!!!??!!!
             :X- M$$$$   •   `"T#$T~!8$WUXU~
            :%`  ~#$$$m:        ~!~ ?$$$$$$
          :!`.-   ~T$$$$8xx.  .xWW- ~""##*"
.....   -~~:<` !    ~?T#$$@@W@*?$$   •  /`
W$@@M!!! .!~~ !!     .:XUW$W!~ `"~:    :
#"~~`.:x%`!!  !H:   !WM$$$$Ti.: .!WUn+!`
:::~:!!`:X~ .: ?H.!u "$$$B$$$!W:U!T$$M~
.~~   :X@!.-~   ?@WTWo("*$$$W$TH$! `
Wi.~!X$?!-~    : ?$$$B$Wu("**$RM!
$R@i.~~ !     :   ~$$$$$B$$en:``
?MXT@Wx.~    :     ~"##*$$$$M~ \033[0m

    ========================================
                Made by protocolhere :)
    ========================================
    1. url scanner
    ========================================
    """
    
    print(text_art)
    
    choice = input("Lütfen bir seçenek seçin: ")
    
    if choice == "1":
        url = input("URL girin: ")
        url_scanner(url)
    else:
        print("Geçersiz seçim. Lütfen 1 numaralı seçeneği seçin.")

if __name__ == "__main__":
    main()
