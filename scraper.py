from selenium import webdriver
from selenium.webdriver.common.by import By
import random
import time
import re
from urllib.parse import urlparse

SKIP_KEYWORDS = ["video", "foto", "infografis", "kolom", "oauth", 
                 "login", "register", "/indeks/"]

BULAN = ["Jan", "Feb", "Mar", "Apr", "Mei", "Jun", 
         "Jul", "Ags", "Sep", "Okt", "Nov", "Des",
         "January", "February", "March", "April", "May", "June",
         "July", "August", "September", "October", "November", "December"]

def ambil_tanggal(driver):
    try:
        time_el = driver.find_element(By.TAG_NAME, "time")
        hasil = time_el.get_attribute("datetime") or time_el.text or ""
        if hasil:
            return hasil
    except:
        pass
    
    semua_el = driver.find_elements(By.XPATH, "//*[contains(text(), '2025') or contains(text(), '2026')]")
    for el in semua_el:
        teks = el.text.strip()
        if any(bln in teks for bln in BULAN) and re.search(r'\d{4}', teks):
            if len(teks) < 60:
                return teks
    return ""

def scrape(url_utama, callback=None, limit=0):
    driver = webdriver.Chrome()
    driver.set_page_load_timeout(30)
    
    try:
        driver.get(url_utama)
    except:
        driver.execute_script("window.stop();")
    
    domain = urlparse(url_utama).netloc

    while True:
        url_indeks = driver.current_url
        news_url_set = set()

        for a in driver.find_elements(By.TAG_NAME, 'a'):
            news_url = a.get_attribute("href")
            if not news_url:
                continue
            if domain not in news_url:
                continue
            if any(skip in news_url for skip in SKIP_KEYWORDS):
                continue
           
            parsed = urlparse(news_url)
            if re.search(r'\d{5}', news_url) and len(parsed.path) > 15:
                news_url_set.add(news_url)

        news_url_list = list(news_url_set)
        count = 0 #Counter artikel

        for url in news_url_list:
            if limit > 0 and count >= limit:
                break #Sudah mencapai limit
            try:
                try:
                    driver.get(url)
                except:
                    driver.execute_script("window.stop();")
                
                time.sleep(random.uniform(1, 3))

                judul = driver.find_element(By.TAG_NAME, "h1").text.strip()
                tanggal = ambil_tanggal(driver)

                paragraf = driver.find_elements(By.TAG_NAME, "p")
                isi = " ".join([p.text for p in paragraf if len(p.text) > 50])

                if not judul or not isi:
                    continue

                data = {"judul": judul, "tanggal": tanggal, "isi": isi, "url": url}
                if callback:
                    lanjut = callback(data)
                    if lanjut is False:
                        driver.quit()
                        return
            
                count += 1 #Tambah counter
                print(f"[{count}] judul   : {judul[:50]}...")
                print(f"[{count}] tanggal : {tanggal}")
                print(f"[{count}] isi     : {isi[:100]}...")

            except Exception as e:
                print(f"Gagal: {e.__class__.__name__}")
                try:
                    driver.execute_script("window.stop();")
                except:
                    pass
                time.sleep(1)

        driver.get(url_indeks)
        time.sleep(random.uniform(1, 2))

        try:
            try:
                next_button = driver.find_element(By.PARTIAL_LINK_TEXT, "Selanjutnya")
            except:
                try:
                    next_button = driver.find_element(By.PARTIAL_LINK_TEXT, "Berikutnya")
                except:
                    next_button = driver.find_element(By.PARTIAL_LINK_TEXT, "Next")
            next_button.click()
            time.sleep(random.uniform(1, 2))
        except:
            break

    driver.quit()


