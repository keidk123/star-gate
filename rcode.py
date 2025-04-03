import pygame
import random
import math
import time

# --- تهيئة Pygame ---
pygame.init()

# --- إعدادات الشاشة ---
screen_width = 800
screen_height = 600
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Space Invaders - نسخة مبسطة")

# --- الألوان ---
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
PURPLE = (128, 0, 128)  # لون بنفسجي للغزاة

# --- تحميل الأصوات ---
pygame.mixer.init()
hit_sound = pygame.mixer.Sound('hit.wav')  # تأكد من وجود هذا الملف في نفس المجلد
# يمكنك استخدام هذا الصوت أو أي صوت آخر متوفر لديك

# --- تحميل صورة البداية ---
try:
    start_image = pygame.image.load('start_image.jpg')  # تأكد من وجود هذا الملف في نفس المجلد
    start_image = pygame.transform.scale(start_image, (screen_width, screen_height))
except pygame.error:
    # إذا لم يتم العثور على الصورة، قم بإنشاء صورة بديلة
    start_image = pygame.Surface((screen_width, screen_height))
    start_image.fill(BLACK)
    title_font = pygame.font.Font('freesansbold.ttf', 64)
    title_text = title_font.render("Space Invaders", True, WHITE)
    start_image.blit(title_text, (screen_width//2 - title_text.get_width()//2, screen_height//2 - title_text.get_height()//2))

# --- متغير لتتبع حالة اللعبة ---
game_state = "start"  # start, play, game_over

# --- إعدادات اللاعب ---
player_width = 50
player_height = 40
player_x = (screen_width - player_width) // 2
player_y = screen_height - player_height - 20
player_speed = 5
player_x_change = 0

# --- إعدادات الغزاة ---
invader_width = 40
invader_height = 30
invader_radius = 20  # نصف قطر الدائرة للغزاة
invader_speed_x = 2 # السرعة الأفقية الأولية
invader_speed_y_drop = 20 # مقدار النزول عند الوصول للحافة
num_invaders_rows = 4
num_invaders_cols = 8
invader_padding = 15 # المسافة بين الغزاة
invaders = []

# إنشاء مصفوفة الغزاة
def create_invaders():
    invaders.clear()
    start_x = 50
    start_y = 50
    for row in range(num_invaders_rows):
        for col in range(num_invaders_cols):
            invader_x = start_x + col * (invader_width + invader_padding)
            invader_y = start_y + row * (invader_height + invader_padding)
            invaders.append(pygame.Rect(invader_x, invader_y, invader_width, invader_height))

create_invaders()
current_invader_speed_x = invader_speed_x # السرعة الحالية للغزاة

# --- إعدادات الرصاصة ---
bullet_width = 5
bullet_height = 15
bullet_speed_y = 10
bullet_x = 0
bullet_y = player_y # تبدأ من عند اللاعب
bullet_state = "ready"  # "ready" - جاهزة للإطلاق, "fire" - تم الإطلاق

# --- النقاط ---
score_value = 0
font = pygame.font.Font('freesansbold.ttf', 32)
text_x = 10
text_y = 10

# --- Game Over ---
game_over_font = pygame.font.Font('freesansbold.ttf', 64)
game_over_flag = False

# --- الساعة للتحكم بسرعة اللعبة ---
clock = pygame.time.Clock()

# --- وقت بدء اللعبة ---
start_time = time.time()

# --- دوال الرسم ---
def draw_player(x, y):
    # رسم مثلث أخضر كبديل للمستطيل
    triangle_points = [
        (x + player_width//2, y),  # رأس المثلث
        (x, y + player_height),     # الزاوية اليسرى السفلية
        (x + player_width, y + player_height)  # الزاوية اليمنى السفلية
    ]
    pygame.draw.polygon(screen, GREEN, triangle_points)

def draw_invader(rect):
    # رسم دائرة بنفسجية بدلاً من المستطيل الأحمر
    center_x = rect.x + rect.width // 2
    center_y = rect.y + rect.height // 2
    pygame.draw.circle(screen, PURPLE, (center_x, center_y), invader_radius)

def draw_bullet(x, y):
    # يمكنك استبدال المستطيل بصورة هنا
    pygame.draw.rect(screen, WHITE, (x, y, bullet_width, bullet_height))

def show_score(x, y):
    score = font.render("Score : " + str(score_value), True, WHITE)
    screen.blit(score, (x, y))

def show_game_over():
    over_text = game_over_font.render("GAME OVER", True, RED)
    text_rect = over_text.get_rect(center=(screen_width / 2, screen_height / 2))
    screen.blit(over_text, text_rect)

# --- دالة التحقق من الاصطدام ---
def is_collision(bullet_rect, invader_rect):
    # حساب مركز الدائرة (الغازي)
    invader_center_x = invader_rect.x + invader_rect.width // 2
    invader_center_y = invader_rect.y + invader_rect.height // 2
    
    # حساب أقرب نقطة من المستطيل (الرصاصة) إلى مركز الدائرة
    closest_x = max(bullet_rect.x, min(invader_center_x, bullet_rect.x + bullet_rect.width))
    closest_y = max(bullet_rect.y, min(invader_center_y, bullet_rect.y + bullet_rect.height))
    
    # حساب المسافة بين أقرب نقطة ومركز الدائرة
    distance_x = invader_center_x - closest_x
    distance_y = invader_center_y - closest_y
    distance = math.sqrt((distance_x ** 2) + (distance_y ** 2))
    
    # إذا كانت المسافة أقل من نصف قطر الدائرة، فهناك اصطدام
    return distance <= invader_radius

# --- دالة إعادة ضبط اللعبة ---
def reset_game():
    global score_value, game_over_flag, bullet_state, player_x, current_invader_speed_x
    score_value = 0
    game_over_flag = False
    bullet_state = "ready"
    player_x = (screen_width - player_width) // 2
    current_invader_speed_x = invader_speed_x
    create_invaders()

# --- حلقة اللعبة الرئيسية ---
running = True
while running:

    # تعبئة الشاشة باللون الأسود في كل إطار
    screen.fill(BLACK)

    # --- معالجة الأحداث (مدخلات المستخدم) ---
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # التعامل مع ضغط الأزرار
        if event.type == pygame.KEYDOWN:
            if game_state == "start" or game_state == "game_over":
                if event.key == pygame.K_SPACE:
                    game_state = "play"
                    reset_game()
                    start_time = time.time()  # إعادة ضبط وقت البداية
            
            if game_state == "play":
                if event.key == pygame.K_LEFT:
                    player_x_change = -player_speed
                if event.key == pygame.K_RIGHT:
                    player_x_change = player_speed
                if event.key == pygame.K_SPACE:
                    if bullet_state == "ready" and not game_over_flag:
                        # إطلاق الرصاصة من منتصف اللاعب
                        bullet_x = player_x + (player_width // 2) - (bullet_width // 2)
                        bullet_y = player_y
                        bullet_state = "fire"

        # التعامل مع رفع الأزرار
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_LEFT or event.key == pygame.K_RIGHT:
                player_x_change = 0

    # --- عرض شاشة البداية ---
    if game_state == "start":
        screen.blit(start_image, (0, 0))
        # التحقق من انتهاء مدة عرض شاشة البداية (2 ثانية)
        if time.time() - start_time >= 2:
            game_state = "play"
        
        pygame.display.update()
        clock.tick(60)
        continue  # تخطي باقي الحلقة

    # --- تحديث حالة اللعبة ---
    if game_state == "play" and not game_over_flag:
        # -- تحديث حركة اللاعب --
        player_x += player_x_change
        # منع اللاعب من الخروج من الشاشة
        if player_x <= 0:
            player_x = 0
        elif player_x >= screen_width - player_width:
            player_x = screen_width - player_width

        # -- تحديث حركة الغزاة --
        move_down = False
        for invader in invaders:
            invader.x += current_invader_speed_x
            # التحقق إذا وصل أي غازي للحافة
            if invader.right >= screen_width or invader.left <= 0:
                move_down = True

        # إذا وصل غازي للحافة، اعكس اتجاه الكل وأنزلهم
        if move_down:
            current_invader_speed_x *= -1 # عكس الاتجاه الأفقي
            for invader in invaders:
                invader.y += invader_speed_y_drop # إنزال الغزاة

        # -- تحديث حركة الرصاصة --
        if bullet_state == "fire":
            bullet_y -= bullet_speed_y
            # إذا خرجت الرصاصة من الشاشة
            if bullet_y <= 0:
                bullet_state = "ready"

        # -- التحقق من الاصطدام (الرصاصة بالغزاة) --
        bullet_rect = pygame.Rect(bullet_x, bullet_y, bullet_width, bullet_height)
        invaders_to_remove = [] # قائمة لتخزين الغزاة الذين تم ضربهم
        if bullet_state == "fire":
            for i, invader in enumerate(invaders):
                if is_collision(bullet_rect, invader):
                    bullet_state = "ready" # إعادة تجهيز الرصاصة
                    bullet_y = player_y + 50 # إبعادها مؤقتًا لتجنب الاصطدام المتعدد
                    score_value += 10
                    invaders_to_remove.append(invader) # إضافة الغازي لقائمة الحذف
                    # تشغيل صوت الاصطدام
                    hit_sound.play()
                    break # يكفي اصطدام واحد للرصاصة

        # إزالة الغزاة الذين تم ضربهم
        for invader in invaders_to_remove:
            invaders.remove(invader)

        # -- التحقق من نهاية اللعبة (وصول الغزاة للاعب) --
        for invader in invaders:
            if invader.bottom >= player_y:
                game_over_flag = True
                game_state = "game_over"
                break # كافٍ غازي واحد لإنهاء اللعبة

        # -- التحقق من الفوز (القضاء على كل الغزاة) --
        if not invaders:
            # يمكنك عرض رسالة فوز هنا أو الانتقال للمستوى التالي
            print("You Win!") # مؤقتًا، طباعة في الطرفية
            # إعادة تهيئة الغزاة لمستوى جديد
            create_invaders()
            current_invader_speed_x = invader_speed_x * 1.2  # زيادة السرعة للمستوى التالي

    # --- الرسم على الشاشة ---

    # رسم اللاعب
    draw_player(player_x, player_y)

    # رسم الغزاة
    for invader in invaders:
        draw_invader(invader)

    # رسم الرصاصة إذا كانت في حالة إطلاق
    if bullet_state == "fire":
        draw_bullet(bullet_x, bullet_y)

    # إظهار النقاط
    show_score(text_x, text_y)

    # إظهار رسالة Game Over إذا انتهت اللعبة
    if game_state == "game_over":
        show_game_over()
        # عرض تعليمات لإعادة اللعب
        restart_text = font.render("Press SPACE to play again", True, WHITE)
        restart_rect = restart_text.get_rect(center=(screen_width / 2, screen_height / 2 + 70))
        screen.blit(restart_text, restart_rect)

    # --- تحديث الشاشة لإظهار كل ما تم رسمه ---
    pygame.display.update()

    # --- تحديد معدل الإطارات (Frames Per Second) ---
    clock.tick(60)  # 60 إطار في الثانية

# --- إنهاء Pygame عند الخروج من الحلقة ---
pygame.quit()
