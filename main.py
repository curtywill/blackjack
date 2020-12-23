"""
Curtiss Williams. Simple blackjack game using pygame and free assets.
"""

import pygame
from pygame.locals import *
from random import randint, shuffle
from sys import exit
import os.path

pygame.init()
DECK = []

WIDTH, HEIGHT = 850, 800
FPS = 60
WHITE = (255, 255, 255)
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("BlackJack")
BG = pygame.image.load(os.path.join("Assets", "background.jpg"))
main_font = pygame.font.SysFont("georgia", 40)

money = 500
bet = 0


def init_deck():
    face_cards = {'A': 11, 'J': 10, 'Q': 10, 'K': 10}
    suits = ['C', 'D', 'H', 'S']
    a = list(face_cards.keys())
    for i in range(2, 11):
        for j in range(0, 4):
            if i < 6:
                DECK.append(Card(a[i - 2] + suits[j], face_cards[a[i - 2]]))
            DECK.append(Card(str(i) + suits[j], i))
    shuffle(DECK)


class Card:
    def __init__(self, sprite_name, value):
        self.sprite_name = sprite_name
        self.sprite = pygame.image.load(os.path.join("Assets", self.sprite_name + ".jpg"))
        self.value = value

    def show(self, x, y):
        WIN.blit(self.sprite, (x, y))

    def get_rank(self):
        return str(self.sprite_name[0])

    def __str__(self):
        return self.sprite_name


class Player:
    def __init__(self):
        self.hand = []
        self.total_value = 0
        self.aces = 0
        self.done = False

    def hit(self):
        index = randint(0, len(DECK) - 1)
        card = DECK.pop(index)
        self.total_value += card.value
        self.hand.append(card)
        if card.get_rank() == "A":
            self.aces += 1
        self.check_aces()

    def bust(self):
        return self.total_value > 21

    def check_aces(self):
        if self.bust():
            if self.aces > 0:
                self.total_value -= 10
                self.aces -= 1

    def blackjack(self):
        return self.total_value == 21

    def deal(self):
        self.hit()
        self.hit()


class User(Player):
    def show_deck(self):
        x, y = 350, HEIGHT - 250
        for i in range(0, len(self.hand)):
            self.hand[i].show(x, y)
            x += 20

    def game_over(self, status: str):
        label = main_font.render(status, 1, WHITE)
        WIN.blit(label, (320, HEIGHT - 325))
        pygame.display.update()
        pygame.time.delay(2000)
        self.done = True


class Dealer(Player):
    def __init__(self):
        super().__init__()
        self.revealed = False
        self.card_back = pygame.image.load(os.path.join("Assets", "green_back.jpg"))

    def show_deck(self):
        x, y = 350, 200
        for i in range(0, len(self.hand)):
            if self.revealed or i == 0:
                self.hand[i].show(x, y)
            else:
                WIN.blit(self.card_back, (x, y))
            x += 20


class Button:
    def __init__(self, x: int, y: int, name=""):
        self.x = x
        self.y = y
        self.name = name
        self.radius = 40
        self.button_font = pygame.font.SysFont("Arial", 20)
        self.label = self.button_font.render(self.name, 1, WHITE)

    def clicked(self):
        mouse_x, mouse_y = pygame.mouse.get_pos()
        if self.x - self.radius <= mouse_x <= self.x + self.radius:
            if self.y - self.radius <= mouse_y <= self.y + self.radius:
                return True
        return False

    def show(self):
        pygame.draw.circle(WIN, (0, 0, 255), (self.x, self.y), self.radius)
        WIN.blit(self.label, (self.x - 20, self.y - 20))


def results(player: User, dealer: Dealer):  # will use this for betting
    d = dealer.bust()
    p = player.bust()
    global money, bet

    if p:
        player.game_over("You lost :(")
        money -= bet
        if money <= 0:
            money = 500
        return

    if not d:
        if player.total_value == dealer.total_value:
            player.game_over("Push")
        elif player.total_value < dealer.total_value:
            money -= bet
            if money <= 0:
                money = 500
            player.game_over("You lost :(")
        else:
            money += bet
            player.game_over("You won!")
    elif d:
        money += bet
        player.game_over("You won!")


def game_loop():
    clock = pygame.time.Clock()
    WIN.blit(BG, (0, 0))
    pygame.display.update()
    
    init_deck()
    bet_buttons = [
        Button(200, 50, "500"),
        Button(350, 50, "1000"),
        Button(500, 50, "2000"),
        Button(650, 50, "5000")
    ]
    hit_button = Button(200, HEIGHT - 300, "Hit")
    stand_button = Button(WIDTH - 200, HEIGHT - 300, "Stand")
    run = True
    has_bet = False
    player = User()
    dealer = Dealer()
    player.deal()
    dealer.deal()
    global money, bet

    def redraw_window():
        clock.tick(FPS)
        WIN.blit(BG, (0, 0))
        WIN.blit(main_font.render('$' + str(money), 1, WHITE), (10, 10))
        WIN.blit(main_font.render(str(player.total_value), 1, WHITE), (200 - 40, HEIGHT - 200))
        player.show_deck()
        dealer.show_deck()
        stand_button.show()
        hit_button.show()
        if not has_bet:
            for b in bet_buttons:
                b.show()
        pygame.display.update()

    while run:
        redraw_window()

        if player.bust() and not player.done:
            player.game_over("Bust")
            dealer.revealed = True
            redraw_window()
            break

        if player.blackjack() and not player.done:
            player.game_over("Blackjack!")

        if len(DECK) == 0:
            init_deck()

        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                exit()
            if event.type == MOUSEBUTTONDOWN:
                if hit_button.clicked() and not player.done:
                    player.hit()
                elif stand_button.clicked():
                    player.done = True
                if not has_bet:
                    for button in bet_buttons:
                        if button.clicked():
                            if int(button.name) <= money:
                                bet = int(button.name)
                                has_bet = True

        if player.done:
            if not dealer.revealed:
                dealer.revealed = True
                redraw_window()
                pygame.time.wait(1000)

            if dealer.total_value < 17:
                dealer.hit()
                pygame.time.wait(1000)
            else:
                break
            redraw_window()

    results(player, dealer)


def main():
    game_loop()
    pygame.event.clear()
    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                exit()
            elif event.type == MOUSEBUTTONDOWN:
                game_loop()


main()
