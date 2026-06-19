import random
import time
from collections import OrderedDict

# Ініціалізація класу Least Recent Used з базовими методами
class LRUCache:
    def __init__(self, capacity=1000):
        self.capacity = capacity
        self.cache = OrderedDict()

    def get(self, key):
        if key not in self.cache:
            return -1

        self.cache.move_to_end(key)
        return self.cache[key]

    def put(self, key, value):
        if key in self.cache:
            self.cache.move_to_end(key)

        self.cache[key] = value

        if len(self.cache) > self.capacity:
            self.cache.popitem(last=False)

# Створення екземпляру класу
cache = LRUCache(capacity=1000)

# Реалізація функції з підрахунку суми без кешування
def range_sum_no_cache(array, left, right):
    return sum(array[left:right + 1])

# Реалізація функції оновлення елементу без кешування
def update_no_cache(array, index, value):
    array[index] = value

# Реалізація функції пошуку у LRU класі
def range_sum_with_cache(array, left, right):
    key = (left, right)

    cached = cache.get(key)

    if cached != -1:
        return cached

    result = sum(array[left:right + 1])
    cache.put(key, result)

    return result

# Реалізація функції оновлення масиву
def update_with_cache(array, index, value):
    array[index] = value

    keys_to_delete = []
    
    # Перебір записів кешу
    for left, right in cache.cache.keys():
        if left <= index <= right:
            keys_to_delete.append((left, right))
    
    # Видаляє всі знайдені ключі для оновлення значень
    for key in keys_to_delete:
        del cache.cache[key]

# Генерує тестові запити. Кількість гарячих діапазонів, які імітуватимуть кешовані дані - 30.
def make_queries(n, q, hot_pool=30, p_hot=0.95, p_update=0.03):
    hot = [
        (random.randint(0, n // 2),
         random.randint(n // 2, n - 1))
        for _ in range(hot_pool)
    ]

    queries = []
    
    # Створення запитів
    for _ in range(q):
        
        # Вибірка для оновлення
        if random.random() < p_update:
            idx = random.randint(0, n - 1)
            val = random.randint(1, 100)
            queries.append(("Update", idx, val))

        else:
            if random.random() < p_hot:
                left, right = random.choice(hot)
            else:
                left = random.randint(0, n - 1)
                right = random.randint(left, n - 1)

            queries.append(("Range", left, right))

    return queries

# Створення тестового масиву, початкових значень та підрахунку
def test_lru_cache():
    n = 100_000
    q = 50_000

    array = [random.randint(1, 100) for _ in range(n)]
    queries = make_queries(n, q)

    array_no_cache = array.copy()
    
    # Тест без кешу
    start = time.perf_counter()

    for query in queries:
        if query[0] == "Range":
            _, left, right = query
            range_sum_no_cache(array_no_cache, left, right)
        else:
            _, idx, value = query
            update_no_cache(array_no_cache, idx, value)

    no_cache_time = time.perf_counter() - start

    array_cache = array.copy()
    
    # Тест з кешем
    start = time.perf_counter()

    for query in queries:
        if query[0] == "Range":
            _, left, right = query
            range_sum_with_cache(array_cache, left, right)
        else:
            _, idx, value = query
            update_with_cache(array_cache, idx, value)

    cache_time = time.perf_counter() - start

    print(f"Без кешу : {no_cache_time:.2f} c")
    print(
        f"LRU-кеш  : {cache_time:.2f} c "
        f"(прискорення ×{no_cache_time / cache_time:.2f})"
    )


if __name__ == "__main__":
    test_lru_cache()