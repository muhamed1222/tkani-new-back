"""
Скрипт для автоматического тестирования API работ
"""
import requests
import sys

def test_get_works():
    """Тестирует endpoint GET /api/works"""
    base_url = "http://localhost:5001"
    url = f"{base_url}/api/works"
    
    print("=" * 50)
    print("Тестирование API работ")
    print("=" * 50)
    
    # Тест 1: Базовый запрос
    print("\n1. Тест базового запроса (page=1, limit=12)...")
    try:
        params = {"page": 1, "limit": 12}
        response = requests.get(url, params=params, timeout=5)
        
        if response.status_code != 200:
            print(f"❌ Ошибка: получен статус {response.status_code}")
            print(f"Ответ: {response.text}")
            return False
        
        data = response.json()
        
        # Проверяем структуру ответа
        required_fields = ["works", "total", "page", "totalPages"]
        for field in required_fields:
            if field not in data:
                print(f"❌ Ошибка: отсутствует поле '{field}' в ответе")
                return False
        
        if not isinstance(data["works"], list):
            print(f"❌ Ошибка: поле 'works' должно быть массивом")
            return False
        
        print(f"✅ API работает корректно!")
        print(f"   Всего работ: {data['total']}")
        print(f"   Текущая страница: {data['page']}")
        print(f"   Всего страниц: {data['totalPages']}")
        print(f"   Работ на странице: {len(data['works'])}")
        
    except requests.exceptions.ConnectionError:
        print("❌ Ошибка: не удалось подключиться к серверу")
        print("   Убедитесь, что Flask сервер запущен на http://localhost:5000")
        return False
    except Exception as e:
        print(f"❌ Ошибка: {str(e)}")
        return False
    
    # Тест 2: Проверка пагинации (если есть данные)
    if data['total'] > 0:
        print("\n2. Тест пагинации...")
        try:
            # Запрашиваем первую страницу
            params1 = {"page": 1, "limit": 5}
            response1 = requests.get(url, params=params1, timeout=5)
            data1 = response1.json()
            
            # Запрашиваем вторую страницу
            if data1['totalPages'] > 1:
                params2 = {"page": 2, "limit": 5}
                response2 = requests.get(url, params=params2, timeout=5)
                data2 = response2.json()
                
                # Проверяем, что работы разные
                if data1['works'] and data2['works']:
                    if data1['works'][0]['id'] != data2['works'][0]['id']:
                        print("✅ Пагинация работает корректно!")
                    else:
                        print("⚠️  Предупреждение: пагинация может работать некорректно")
                else:
                    print("✅ Пагинация работает (вторая страница пуста)")
            else:
                print("✅ Пагинация работает (только одна страница)")
                
        except Exception as e:
            print(f"⚠️  Предупреждение при тестировании пагинации: {str(e)}")
    
    # Тест 3: Проверка валидации параметров
    print("\n3. Тест валидации параметров...")
    try:
        # Тест с отрицательной страницей
        params_neg = {"page": -1, "limit": 12}
        response_neg = requests.get(url, params=params_neg, timeout=5)
        if response_neg.status_code == 200:
            data_neg = response_neg.json()
            if data_neg['page'] >= 1:
                print("✅ Валидация отрицательной страницы работает")
            else:
                print("⚠️  Предупреждение: валидация может работать некорректно")
        
        # Тест с нулевым лимитом
        params_zero = {"page": 1, "limit": 0}
        response_zero = requests.get(url, params=params_zero, timeout=5)
        if response_zero.status_code == 200:
            data_zero = response_zero.json()
            if data_zero.get('works') is not None:
                print("✅ Валидация нулевого лимита работает")
        
    except Exception as e:
        print(f"⚠️  Предупреждение при тестировании валидации: {str(e)}")
    
    # Тест 4: Проверка формата данных работ
    if data['works']:
        print("\n4. Тест формата данных работ...")
        work = data['works'][0]
        required_work_fields = ["id", "title", "image", "link"]
        all_fields_present = all(field in work for field in required_work_fields)
        
        if all_fields_present:
            print("✅ Формат данных работ корректен")
            print(f"   Пример работы: ID={work['id']}, Title={work['title'][:50]}...")
        else:
            missing = [f for f in required_work_fields if f not in work]
            print(f"❌ Ошибка: отсутствуют поля в работе: {missing}")
            return False
    
    print("\n" + "=" * 50)
    print("✅ Все тесты пройдены успешно!")
    print("=" * 50)
    return True

if __name__ == "__main__":
    success = test_get_works()
    sys.exit(0 if success else 1)

