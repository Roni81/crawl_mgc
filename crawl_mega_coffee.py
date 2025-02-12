import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime

class GetInfoMenus:
    def __init__(self):
        self.base_url = 'https://www.mega-mgccoffee.com/menu/menu.php'
    
    def get_soup(self, page):
        """페이지별 BeautifulSoup 객체 반환"""
        params = {
            'page': page,
            'menu_category1': 1,
            'menu_category2': 1,
            'category': '',
            'list_checkbox_all': 'all'
        }
        
        try:
            response = requests.get(self.base_url, params=params)
            response.raise_for_status()
            return BeautifulSoup(response.text, 'html.parser')
        except requests.RequestException as e:
            print(f"페이지 {page} 요청 실패: {e}")
            return None
    
    def get_titles(self, soup):
        """메뉴 한글명 추출"""
        titles = []
        for title in range(0, len(soup.select('div b')), 2):
            soup_ele = soup.select('div b')[title].text
            titles.append(soup_ele)
        return titles
    
    def get_ice_hot(self, soup):
        """ICE/HOT 정보 추출"""
        return [temp.text for temp in soup.select('div.cont_gallery_list_label')]
    
    def get_titles_eng(self, soup):
        """메뉴 영문명 추출"""
        titles_eng = []
        for title_en in range(1, len(soup.select('div.text1'))+1, 2):
            soup_ele = soup.select('div.text1')[title_en].text.replace('\t','').replace('\n','')
            titles_eng.append(soup_ele)
        return titles_eng
    
    def get_sizes(self, soup):
        """사이즈 정보 추출"""
        sizes = []
        for size in range(4, len(soup.select('div.cont_text > div.cont_text_inner')), 6):
            cont = soup.select('div.cont_text > div.cont_text_inner')[size].text.replace('\t','').replace('\n','')
            sizes.append(cont)
        return sizes
    
    def get_kcals(self, soup):
        """칼로리 정보 추출"""
        kcals = []
        for kcal in range(5, len(soup.select('div.cont_text > div.cont_text_inner')), 6):
            cal = soup.select('div.cont_text > div.cont_text_inner')[kcal].text.replace('\t','').replace('\n','')
            kcals.append(float(cal.split(' ')[2].split('k')[0]))
        return kcals
    

    def get_sugar_categories(self, soup):

        sugar_cat = []
        for kcal in range(5, len(soup.select('div.cont_text > div.cont_text_inner')), 6):
            cal = soup.select('div.cont_text > div.cont_text_inner')[kcal].text.replace('\t','').replace('\n','')
            if cal >= 50:
                sugar_cat.append('yes')
            else:
                sugar_cat.append('no')
        return sugar_cat

    
    def get_nutrients(self, soup):
        """영양정보 추출 (지방, 탄수화물, 나트륨, 단백질, 카페인)"""
        fats, cars, sodiums, proteins, caffeines = [], [], [], [], []
        
        for freq in range(0, len(soup.select('div.cont_list_small2 li')), 5):
            fat_temp = soup.select('div.cont_list_small2 li')[freq].text.split(' ')[1].split('g')[0]
            car_temp = soup.select('div.cont_list_small2 li')[freq+1].text.split(' ')[1].split('g')[0]
            sod_temp = soup.select('div.cont_list_small2 li')[freq+2].text.split(' ')[1].split('mg')[0]
            prot_temp = soup.select('div.cont_list_small2 li')[freq+3].text.split(' ')[1].split('g')[0]
            caff_temp = soup.select('div.cont_list_small2 li')[freq+4].text.replace('\n','').replace('\t','').replace('카페인','').replace('mg','').strip()
            
            

            fats.append(float(fat_temp))
            cars.append(float(car_temp))
            sodiums.append(float(sod_temp))
            proteins.append(float(prot_temp))
            caffeines.append(float(caff_temp if caff_temp != '' else '0.0'))
       
            
        return fats, cars, sodiums, proteins, caffeines
    

    def get_img_urls(self, soup):
        
        img_urls = []
        for img_url in soup.select('img'):
            img_urls.append(img_url.attrs['src'])

        return img_urls

    
    def get_page_info(self, page):
        """한 페이지의 모든 정보 추출"""
        soup = self.get_soup(page)
        if not soup:
            return None
            
        return {
            'titles': self.get_titles(soup),
            'ice_hot': self.get_ice_hot(soup),
            'titles_eng': self.get_titles_eng(soup),
            'sizes': self.get_sizes(soup),
            'kcals': self.get_kcals(soup),
            'img_urls': self.get_img_urls(soup),
            'nutrients': self.get_nutrients(soup)
        }

    def combine_all_pages(self, start_page=1, end_page=3):
        """여러 페이지의 정보를 수집하여 통합"""
        all_titles = []
        all_ice_hot = []
        all_titles_eng = []
        all_sizes = []
        all_kcals = []
        all_fats = []
        all_cars = []
        all_sodiums = []
        all_proteins = []
        all_caffeines = []
        all_img_urls = []
        all_sugar_cat = []

        for page in range(start_page, end_page + 1):
            print(f"페이지 {page} 크롤링 중...")
            info = self.get_page_info(page)
            if info:
                all_titles.extend(info['titles'])
                all_ice_hot.extend(info['ice_hot'])
                all_titles_eng.extend(info['titles_eng'])
                all_sizes.extend(info['sizes'])
                all_kcals.extend(info['kcals'])
                all_sugar_cat.extend(info['sugar_cat'])
                all_img_urls.extend(info['img_urls'])
                
                fats, cars, sodiums, proteins, caffeines = info['nutrients']
                all_fats.extend(fats)
                all_cars.extend(cars)
                all_sodiums.extend(sodiums)
                all_proteins.extend(proteins)
                all_caffeines.extend(caffeines)

        # 각 상품별로 정보를 묶어서 리스트 생성
        products = []
        for i in range(len(all_titles)):
            product = {
                'id': i + 1,
                'title': all_titles[i],
                'temperature': all_ice_hot[i],
                'title_eng': all_titles_eng[i],
                'size': all_sizes[i],
                'img_urls': all_img_urls[i],

                'nutrition': {
                    'kcal': all_kcals[i],
                    'fat': all_fats[i],
                    'carbohydrate': all_cars[i],
                    'sodium': all_sodiums[i],
                    'protein': all_proteins[i],
                    'caffeine': all_caffeines[i]
                }
            }
            products.append(product)

        return products

    def save_to_json(self, products, filename=None):
        """상품 정보를 JSON 파일로 저장"""
        if filename is None:
            filename = f"mega_mgc_menus_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        data = {
            "meta": {
                "created_at": datetime.now().isoformat(),
                "total_products": len(products),
                "source": "MEGA MGC COFFEE"
            },
            "products": products
        }
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            print(f"데이터가 '{filename}'에 성공적으로 저장되었습니다.")
            return True
        except Exception as e:
            print(f"파일 저장 중 오류 발생: {e}")
            return False