from random import randint
import pygame as pg

# Константы для размеров поля и сетки:
SCREEN_WIDTH, SCREEN_HEIGHT = 640, 480
GRID_SIZE = 20
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE

# Направления движения:
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

# Цвет фона - черный:
BOARD_BACKGROUND_COLOR = (0, 0, 0)

# Цвет границы ячейки
BORDER_COLOR = (93, 216, 228)

# Цвет яблока
APPLE_COLOR = (255, 0, 0)

# Цвет змейки
SNAKE_COLOR = (0, 255, 0)

# Цвет камня
STONE_COLOR = (234, 230, 202)

# Цвет счета
LIGHT_YELLOW = (255, 255, 224)

# Цвет золотого яблока
GOLD_APPLE = (255, 255, 0)

# Скорость движения змейки:
SPEED = 10

# Настройка игрового окна:
screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)

# Заголовок окна игрового поля:
pg.display.set_caption('Змейка')

# Настройка времени:
clock = pg.time.Clock()


class GameObject:
    """Базовый класс для всех игровых объектов."""

    def __init__(self, body_color=None):
        self.position = None
        self.body_color = body_color

    def randomize_position(self, occupied_positions=None):
        """Устанавливает случайное положение объекта."""
        if occupied_positions is None:
            occupied_positions = []

        while True:
            self.position = (
                randint(0, GRID_WIDTH - 1) * GRID_SIZE,
                randint(0, GRID_HEIGHT - 1) * GRID_SIZE
            )
            if self.position not in occupied_positions:
                break

    def draw(self):
        """Отрисовывает объект на экране."""
        rect = pg.Rect(self.position, (GRID_SIZE, GRID_SIZE))
        pg.draw.rect(screen, self.body_color, rect)
        pg.draw.rect(screen, BORDER_COLOR, rect, 1)


class Stone(GameObject):
    """Класс Камень."""

    def __init__(self):
        super().__init__(body_color=STONE_COLOR)


class Apple(GameObject):
    """Класс Яблоко."""

    def __init__(self):
        super().__init__(body_color=APPLE_COLOR)


class GoldApple(GameObject):
    """Класс Золотое Яблоко."""

    def __init__(self):
        super().__init__(body_color=GOLD_APPLE)


class Snake(GameObject):
    """Класс Змейка."""

    def __init__(self):
        super().__init__(body_color=SNAKE_COLOR)
        self.reset()
        self.last = None

    def reset(self):
        """Сбрасывает змейку в начальное состояние."""
        self.length = 1
        self.positions = [((SCREEN_WIDTH // 2), (SCREEN_HEIGHT // 2))]
        self.direction = RIGHT
        self.next_direction = None

    def get_head_position(self):
        """Возвращает позицию головы змейки."""
        return self.positions[0]

    def move(self):
        """Обновляет позицию змейки."""
        head = self.get_head_position()
        x, y = self.direction
        new_head = ((head[0] + x * GRID_SIZE) % SCREEN_WIDTH,
                    (head[1] + y * GRID_SIZE) % SCREEN_HEIGHT)
        self.positions.insert(0, new_head)

        if len(self.positions) > self.length:
            self.last = self.positions.pop()
        else:
            self.last = None

    def draw(self):
        """Отрисовывает змейку на экране."""
        for position in self.positions:
            rect = pg.Rect(position, (GRID_SIZE, GRID_SIZE))
            pg.draw.rect(screen, self.body_color, rect)
            pg.draw.rect(screen, BORDER_COLOR, rect, 1)

        # Затирание последнего сегмента
        if self.last:
            last_rect = pg.Rect(self.last, (GRID_SIZE, GRID_SIZE))
            pg.draw.rect(screen, BOARD_BACKGROUND_COLOR, last_rect)

    def update_direction(self):
        """Обновляет направление движения змейки."""
        if self.next_direction:
            self.direction = self.next_direction
            self.next_direction = None


def handle_keys(game_object):
    """Обрабатывает нажатия клавиш для изменения направления."""
    for event in pg.event.get():
        if event.type == pg.QUIT:
            pg.quit()
            raise SystemExit
        elif event.type == pg.KEYDOWN:
            if event.key == pg.K_UP and game_object.direction != DOWN:
                game_object.next_direction = UP
            elif event.key == pg.K_DOWN and game_object.direction != UP:
                game_object.next_direction = DOWN
            elif event.key == pg.K_LEFT and game_object.direction != RIGHT:
                game_object.next_direction = LEFT
            elif event.key == pg.K_RIGHT and game_object.direction != LEFT:
                game_object.next_direction = RIGHT


font_name = pg.font.match_font('arial')


def draw_text(surf, text, size, x, y):
    """Отрисовывает текст на экране."""
    font = pg.font.Font(font_name, size)
    text_surface = font.render(text, True, LIGHT_YELLOW)
    text_rect = text_surface.get_rect()
    text_rect.midtop = (x, y)
    surf.blit(text_surface, text_rect)


def init_game():
    """Инициализация игровых объектов."""
    apple = Apple()
    apple.randomize_position()
    snake = Snake()
    stones = [Stone()]
    for stone in stones:
        stone.randomize_position()
    gold_apples = []
    score = 0
    return apple, snake, stones, gold_apples, score


def draw_object(screen, apple, snake, stones, gold_apples, score):
    """Отрисовка объектов на экране."""
    screen.fill(BOARD_BACKGROUND_COLOR)
    apple.draw()
    snake.draw()
    for stone in stones:
        stone.draw()
    for gold_apple in gold_apples:
        gold_apple.draw()
    draw_text(screen, f'Счет: {score}', 18, SCREEN_WIDTH / 2, 10)
    pg.display.update()


def main():
    """Основной цикл игры."""
    pg.init()
    apple, snake, stones, gold_apples, score = init_game()

    while True:
        clock.tick(SPEED)

        # Обработка событий
        handle_keys(snake)

        # Движение змейки
        snake.move()
        snake.update_direction()

        # Проверка коллизий
        head = snake.get_head_position()

        # Съедание яблока
        if head == apple.position:
            snake.length += 1
            score += 1
            apple.randomize_position(snake.positions)

            # Добавление камня каждые 5 очков
            if score % 5 == 0:
                n_stone = Stone()
                n_stone.randomize_position(snake.positions + [apple.position])
                stones.append(n_stone)

            # Добавление золотого яблока каждые 10 очков
            if score % 10 == 0:
                ng_apple = GoldApple()
                ng_apple.randomize_position(snake.positions + [apple.position])
                gold_apples.append(ng_apple)

        # Съедание золотого яблока
        for gold_apple in gold_apples:
            if head == gold_apple.position:
                score += 3
                gold_apples.remove(gold_apple)
                stones = []

        # Столкновение с собой или камнем
        if (head in snake.positions[3:]
                or any(head == stone.position for stone in stones)):
            snake.reset()
            score = 0
            stones = [Stone()]
            for stone in stones:
                stone.randomize_position()
            gold_apples = []
            apple.randomize_position(snake.positions)

        # Отрисовка
        draw_object(screen, apple, snake, stones, gold_apples, score)


if __name__ == '__main__':
    main()
