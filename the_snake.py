from random import choice, randint

import pygame as pg

import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO)

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


def draw_dialog(screen, image_path):
    """Отрисовывает диалоговое окно с текстом, картинкой и кнопкой."""
    dialog_width = 250  # Ширина диалогового окна для картинки
    dialog_height = 250  # Высота диалогового окна для картинки
    dialog_x = (SCREEN_WIDTH - dialog_width) // 2
    dialog_y = (SCREEN_HEIGHT - dialog_height) // 2
    text_size = 24
    text = 'Камень я не дам'
    width_button = 150
    height_button = 40

    # Отрисовка фона диалогового окна
    dialog_rect = pg.Rect(dialog_x, dialog_y, dialog_width, dialog_height)
    pg.draw.rect(screen, BOARD_BACKGROUND_COLOR, dialog_rect)
    pg.draw.rect(screen, BORDER_COLOR, dialog_rect, 2)

    # Загрузка и отрисовка картинки
    try:
        image = pg.image.load(image_path)  # Загружаем изображение
        image = pg.transform.scale(image, (200, 100))  # Масштабируем его
        image_rect = image.get_rect(
            center=(dialog_x + dialog_width // 2, dialog_y + 70))
        screen.blit(image, image_rect)
    except pg.error as e:
        logging(f"Ошибка загрузки изображения: {e}")

    # Отрисовка кнопки "Рестарт"
    button_rect = pg.Rect(dialog_x + 50, dialog_y + 180,
                          width_button, height_button)
    pg.draw.rect(screen, BOARD_BACKGROUND_COLOR, button_rect)
    pg.draw.rect(screen, BORDER_COLOR, button_rect, 2)

    button_font = pg.font.Font(None, text_size)
    button_text = button_font.render(text, True, LIGHT_YELLOW)
    button_text_rect = button_text.get_rect(center=button_rect.center)
    screen.blit(button_text, button_text_rect)

    return button_rect


def handle_dialog_events(button_rect):
    """Обрабатывает события в диалоговом окне."""
    for event in pg.event.get():
        if event.type == pg.QUIT:
            pg.quit()
            raise SystemExit
        elif event.type == pg.MOUSEBUTTONDOWN:
            # Проверяем, была ли нажата кнопка "Рестарт"
            if button_rect.collidepoint(event.pos):
                return True  # Игрок нажал "Рестарт"
    return False


class GameObject:
    """Базовый класс для всех игровых объектов."""

    def __init__(self, body_color=None, position=None):
        self.position = position
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
        raise NotImplementedError(
            'Метод draw() должен быть переопределен в дочернем классе.')


def draw_cell(position, body_color):
    """Отрисовывает ячейку на экране."""
    rect = pg.Rect(position, (GRID_SIZE, GRID_SIZE))
    pg.draw.rect(screen, body_color, rect)
    pg.draw.rect(screen, BORDER_COLOR, rect, 1)


class Stone(GameObject):
    """Класс Камень."""

    def __init__(self):
        super().__init__(body_color=STONE_COLOR)

    def draw(self):
        """Отрисовывает камень на экране."""
        draw_cell(self.position, self.body_color)


class Apple(GameObject):
    """Класс Яблоко."""

    def __init__(self):
        super().__init__(body_color=APPLE_COLOR)

    def draw(self):
        """Отрисовывает яблоко на экране."""
        draw_cell(self.position, self.body_color)


class GoldApple(GameObject):
    """Класс Золотое Яблоко."""

    def __init__(self):
        super().__init__(body_color=GOLD_APPLE)

    def draw(self):
        """Отрисовывает золотое яблоко на экране."""
        draw_cell(self.position, self.body_color)


class Snake(GameObject):
    """Класс Змейка."""

    def __init__(self):
        super().__init__(body_color=SNAKE_COLOR)
        self.reset()

    def reset(self):
        """Сбрасывает змейку в начальное состояние."""
        self.length = 1
        self.last = None
        self.positions = [((SCREEN_WIDTH // 2), (SCREEN_HEIGHT // 2))]
        self.direction = choice([LEFT, RIGHT, UP, DOWN])
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
            draw_cell(position, self.body_color)

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
    size_text = 18
    text_y = 10
    for stone in stones:
        stone.draw()
    for gold_apple in gold_apples:
        gold_apple.draw()
    draw_text(screen, f'Счет: {score}', size_text, SCREEN_WIDTH / 2, text_y)
    pg.display.update()


def main():
    """Основной цикл игры."""
    pg.init()
    apple, snake, stones, gold_apples, score = init_game()
    game_over = False
    game_over_image = "stone2.jpg"
    stone_spawn_intervall = 5
    gold_apple_spawn_intervall = 10

    while True:
        clock.tick(SPEED)

        if not game_over:
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
                if score % stone_spawn_intervall == 0:
                    n_stone = Stone()
                    n_stone.randomize_position(
                        snake.positions + [apple.position])
                    stones.append(n_stone)

                # Добавление золотого яблока каждые 10 очков
                if score % gold_apple_spawn_intervall == 0:
                    ng_apple = GoldApple()
                    ng_apple.randomize_position(
                        snake.positions + [apple.position])
                    gold_apples.append(ng_apple)

            # Съедание золотого яблока
            for gold_apple in gold_apples:
                if head == gold_apple.position:
                    score += 3
                    gold_apples.remove(gold_apple)
                    stones = []

            # Столкновение с собой или камнем
            if (head in snake.positions[4:]
                    or any(head == stone.position for stone in stones)):
                game_over = True

            # Отрисовка
            draw_object(screen, apple, snake, stones, gold_apples, score)
        else:
            # Отображение диалогового окна с картинкой
            button_rect = draw_dialog(screen, game_over_image)
            if handle_dialog_events(button_rect):
                # Рестарт игры
                apple, snake, stones, gold_apples, score = init_game()
                game_over = False

        pg.display.update()


if __name__ == '__main__':
    main()
