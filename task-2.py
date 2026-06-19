import random
import time
from collections import deque
from typing import Dict

# Ініціалізація класу ковзного вікна з лімітуванням у один запит на 10 секунд
class SlidingWindowRateLimiter:
    def __init__(self, window_size: int = 10, max_requests: int = 1):
        self.window_size = window_size
        self.max_requests = max_requests
        self.users: Dict[str, deque] = {}

    # Видаляє усі повідомлення, старші за розмір вікна
    def _cleanup_window(self, user_id: str, current_time: float) -> None:

        if user_id not in self.users:
            return
        
        # Беру чергу повідомлень
        window = self.users[user_id]

        # Перевіряю чи повідомлення застаріле (довше, ніж вікно очікування) і якщо так, то видаляю його
        while window and current_time - window[0] >= self.window_size:
            window.popleft()
        
        # За відсутності повідомлень видаляю користувача зі словника
        if not window:
            del self.users[user_id]

    # Перевіряє чи може користувач зараз надіслати повідомлення
    def can_send_message(self, user_id: str) -> bool:

        current_time = time.time()
        
        # Очищаю старі повідомлення перед новим дозволом для лише актуальних повідомлень
        self._cleanup_window(user_id, current_time)

        if user_id not in self.users:
            return True

        return len(self.users[user_id]) < self.max_requests

    # Здійснює запис повідомлень
    def record_message(self, user_id: str) -> bool:

        current_time = time.time()
        
        # Знову ж таки очищаю старі записи, а також перевіряю дозвіл на надсилання повідомлень
        self._cleanup_window(user_id, current_time)

        if not self.can_send_message(user_id):
            return False

        if user_id not in self.users:
            self.users[user_id] = deque()
        
        # Якщо всі умови затверджено, додається поточний час та дозвіл на надсилання повідомлення
        self.users[user_id].append(current_time)

        return True
    
    # Реалізує коментар стосовно необхідного часу очікування
    def time_until_next_allowed(self, user_id: str) -> float:

        current_time = time.time()

        self._cleanup_window(user_id, current_time)
        
        # Якщо користувача немає, то час очікування не потрібен, а тому виставлений на 0
        if user_id not in self.users:
            return 0.0
        
        # Виявляю найстаріше повідомлення і здійснюю підрахунок часу очікування
        oldest_message = self.users[user_id][0]

        wait_time = self.window_size - (current_time - oldest_message)

        return max(0.0, wait_time)

# Реалізація тестування
def test_rate_limiter():

    limiter = SlidingWindowRateLimiter(
        window_size=10,
        max_requests=1
    )

    print("\n=== Симуляція потоку повідомлень ===")

    for message_id in range(1, 11):

        user_id = message_id % 5 + 1

        result = limiter.record_message(str(user_id))
        wait_time = limiter.time_until_next_allowed(str(user_id))

        print(
            f"Повідомлення {message_id:2d} | "
            f"Користувач {user_id} | "
            f"{'✓' if result else f'× (очікування {wait_time:.1f}с)'}"
        )

        time.sleep(random.uniform(0.1, 1.0))

    print("\nОчікуємо 4 секунди...")
    time.sleep(4)

    print("\n=== Нова серія повідомлень після очікування ===")

    for message_id in range(11, 21):

        user_id = message_id % 5 + 1

        result = limiter.record_message(str(user_id))
        wait_time = limiter.time_until_next_allowed(str(user_id))

        print(
            f"Повідомлення {message_id:2d} | "
            f"Користувач {user_id} | "
            f"{'✓' if result else f'× (очікування {wait_time:.1f}с)'}"
        )

        time.sleep(random.uniform(0.1, 1.0))


if __name__ == "__main__":
    test_rate_limiter()