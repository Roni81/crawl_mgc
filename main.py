from crawl_mega_coffee import GetInfoMenus
import argparse
from datetime import datetime

def main():
    # 명령행 인자 파서 설정
    parser = argparse.ArgumentParser(description='MEGA MGC COFFEE 메뉴 정보 크롤러')
    parser.add_argument('--start', type=int, default=1, help='시작 페이지 번호 (기본값: 1)')
    parser.add_argument('--end', type=int, default=3, help='끝 페이지 번호 (기본값: 3)')
    parser.add_argument('--output', type=str, help='저장할 파일명 (기본값: 자동 생성)')
    
    args = parser.parse_args()

    try:
        # 크롤러 초기화
        crawler = GetInfoMenus()
        
        print("크롤링 시작...")
        print(f"페이지 범위: {args.start} ~ {args.end}")
        
        # 데이터 수집
        all_products = crawler.combine_all_pages(args.start, args.end)
        print(f"총 {len(all_products)}개의 메뉴 정보를 수집했습니다.")
        
        # 파일명 설정
        filename = args.output
        if not filename:
            filename = f"mega_mgc_menus_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        # JSON 파일로 저장
        if crawler.save_to_json(all_products, filename):
            print("크롤링이 성공적으로 완료되었습니다.")
        else:
            print("파일 저장 중 오류가 발생했습니다.")
            
    except Exception as e:
        print(f"오류 발생: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())

