##########################################################################
##Program Author: George Zhang                                          ##
##Revision Date: Jan 17, 2019                                           ##
##Program Name: online_pong.py                                          ##
##Description: This program lets users play a game of online pong.      ##
##########################################################################

##########################################################################
#                                                                        #
# NOTE: To run this code properly, you MUST need Python 3.7.1+. -George  #
#                                                                        #
##########################################################################

##########################################################################
#                                                                        #
#         To win this game, get the higher score in 10 matches.          #
#                                                                        #
##########################################################################

# importation of modules
import math as m
import random
import asyncio
import socket
import pygame
from pygame.locals import *

# get image with background removed
def remove_background(image, background=None):
    """Return image with transparent background."""
    image = image.copy()
    if background is None:
        background = image.get_at((0, 0))
    image.set_colorkey(background)
    return image.convert()
# end remove_background

# draw images
def draw_image(screen, image, x, y, angle=0):
    """Draw image on the screen at specified coordinates."""
    image = image.copy()
    if angle != 0:
        image = pygame.transform.rotate(image, m.degrees(angle))
    screen.blit(
        image,
        (
            x - image.get_width()/2,
            y - image.get_height()/2
        )
    )
# end draw_player

def draw_text(
    screen, x, y, text,
    name='freesansbold.ttf',
    size=35,
    colour=(0, 0, 0),
    angle=0,
):
    """Draw text on the screen at specified coordinates."""
    font = pygame.font.Font(name, size)
    text_obj = font.render(text, True, colour)
    draw_image(screen, text_obj, x, y, angle)
# end draw_text

# main function that runs all code
def main():
    # initialize all functions / modules
    pygame.init()

    # colours
    SCREEN_WIDTH = 800 # width of window
    SCREEN_HEIGHT = 600 # height of window
    WHITE = (255, 255, 255)
    RED = (255, 0, 0)
    BLACK = (0, 0, 0)
    BUTTON = (166, 200, 100)
    BACKGROUND = (124, 124, 180)

    # make window
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT)) # size
    pygame.display.set_caption('Online Pong') # title

    # make variables
    clock = pygame.time.Clock() # make screen clock
    high_score = 0
    game_exit = False
    debug = [0, '']

    # loop
    while not game_exit:
        # default screen background
        screen.fill(BACKGROUND)

        # make buttons
        def draw_button(x, y, w, h, text, size=50, **kwargs):
            pygame.draw.rect(
                screen, BUTTON,
                (
                    SCREEN_WIDTH*x, SCREEN_HEIGHT*y,
                    SCREEN_WIDTH*w, SCREEN_HEIGHT*h
                )
            )
            draw_text(
                screen,
                SCREEN_WIDTH*(x + w/2),
                SCREEN_HEIGHT*(y + h/2 + 0.005),
                text,
                size=50,
                **kwargs
            )
        # end draw_button
        draw_button(0.3, 0.4, 0.4, 0.1, 'SINGLE')
        draw_button(0.3, 0.55, 0.4, 0.1, 'LOCAL')
        draw_button(0.3, 0.7, 0.4, 0.1, 'ONLINE')
        draw_button(0.3, 0.85, 0.4, 0.1, 'QUIT')
        draw_text(
            screen,
            SCREEN_WIDTH*0.5,
            SCREEN_HEIGHT*0.15,
            'Online Pong',
            size = 120
        )
        draw_text(
            screen,
            SCREEN_WIDTH*0.5,
            SCREEN_HEIGHT*0.3,
            f'HI: {high_score}',
            size = 50
        )
        draw_text(
            screen,
            SCREEN_WIDTH*0.5,
            SCREEN_HEIGHT*0.36,
            'To win this game, get the higher score in 10 matches :D',
            size = 24
        )

        # error message
        debug[0] = max(debug[0] - 1, 0)
        if debug[0] > 0 and debug[1]:
            pygame.draw.rect(
                screen, RED,
                (
                    SCREEN_WIDTH*0.15, SCREEN_HEIGHT*0.1,
                    SCREEN_WIDTH*0.7, SCREEN_HEIGHT*0.1
                )
            )
            try:
                debug[2]
            except:
                debug = debug + [50]
            draw_text(
                screen,
                SCREEN_WIDTH*0.5,
                SCREEN_HEIGHT*0.155,
                debug[1],
                size = debug[2]
            )

        # update screen
        pygame.display.update()

        # event checking
        for event in pygame.event.get():
            if event.type == MOUSEBUTTONDOWN:
                x, y = event.pos
                if SCREEN_WIDTH*0.3 < x < SCREEN_WIDTH*0.7:
                    if SCREEN_HEIGHT*0.4 < y < SCREEN_HEIGHT*0.5:
                        out = local(screen, ai = True)
                        if out[0] is not None:
                            high_score = out[0]
                        debug = out[1]
                    elif SCREEN_HEIGHT*0.55 < y < SCREEN_HEIGHT*0.65:
                        out = local(screen)
                        if out[0] is not None:
                            high_score = out[0]
                        debug = out[1]
                    elif SCREEN_HEIGHT*0.7 < y < SCREEN_HEIGHT*0.8:
                        out = online(screen)
                        if out[0] is not None:
                            high_score = out[0]
                        debug = out[1]
                    elif SCREEN_HEIGHT*0.85 < y < SCREEN_HEIGHT*0.95:
                        pygame.quit()
                        game_exit = True
                        break
            elif event.type == QUIT:
                pygame.quit()
                game_exit = True
                break
        # end for

        clock.tick(60) # 60 fps
    # end while
# end main()

# local multiplayer code
def local(screen, ai=False):
    # colours
    SCREEN_WIDTH = 800 # width of window
    SCREEN_HEIGHT = 600 # height of window
    WHITE = (255, 255, 255)
    RED = (255, 0, 0)
    BLACK = (0, 0, 0)
    BUTTON = (166, 200, 100)
    BACKGROUND = (124, 124, 180)

    # game variables
    clock = pygame.time.Clock() # make screen clock
    matches = 0
    paused = False
    points = 0
    player1 = 0
    player2 = 0
    player1_paddle = SCREEN_HEIGHT*0.5
    player2_paddle = SCREEN_HEIGHT*0.5
    player1_speed = 0
    player2_speed = 0
    player1_size = SCREEN_HEIGHT*0.075
    player2_size = SCREEN_HEIGHT*0.075
    speed = (SCREEN_WIDTH + SCREEN_WIDTH)/2*0.005 # 0.005
    balls = (SCREEN_WIDTH + SCREEN_WIDTH)/2*0.005
    ballx = SCREEN_WIDTH/2
    bally = SCREEN_HEIGHT/2
    ballr = (SCREEN_WIDTH + SCREEN_WIDTH)/2*0.01
    balld = random.randint(1, 360)
    delay = 60
    while 75 < balld < 105 or 255 < balld < 285:
        balld = random.randint(1, 360)
    balln = balld

    # ai variables
    if ai:
        reaction = 40
        direction = 0
        error = None

    # loop
    while matches < 10:
        # default screen background
        screen.fill(BACKGROUND)

        # event checking
        for event in pygame.event.get():
            if event.type == KEYDOWN:
                if event.key == K_w:
                    player1_speed += -speed
                elif event.key == K_s:
                    player1_speed += speed
                elif event.key == K_ESCAPE:
                    paused = not paused
                elif not ai:
                    if event.key == K_UP:
                        player2_speed += -speed
                    elif event.key == K_DOWN:
                        player2_speed += speed
                elif ai:
                    if event.key == K_UP:
                        player1_speed += -speed
                    elif event.key == K_DOWN:
                        player1_speed += speed
            elif event.type == KEYUP:
                if event.key == K_w:
                    player1_speed -= -speed
                elif event.key == K_s:
                    player1_speed -= speed
                elif not ai:
                    if event.key == K_UP:
                        player2_speed -= -speed
                    elif event.key == K_DOWN:
                        player2_speed -= speed
                elif ai:
                    if event.key == K_UP:
                        player1_speed -= -speed
                    elif event.key == K_DOWN:
                        player1_speed -= speed
            elif paused and event.type == MOUSEBUTTONDOWN:
                x, y = event.pos
                if SCREEN_WIDTH*0.35 < x < SCREEN_WIDTH*0.65:
                    if SCREEN_HEIGHT*0.45 < y < SCREEN_HEIGHT*0.55:
                        paused = not paused
                    if SCREEN_HEIGHT*0.6 < y < SCREEN_HEIGHT*0.7:
                        matches = 21
                        break
            elif event.type == QUIT:
                matches = 21
                break
        # end for

        # break loop if quit
        if matches == 21:
            break

        # paused menu
        if paused:
            pass
        else:
            # decrement delay
            delay = max(delay - 1, 0)

            # ai calculations
            if ai:
                reaction = max(reaction - 1, 0)
                if delay > 0:
                    error = None
                if 90 < balld%360 < 270:
                    player2_speed = 0
                    error = None
                elif reaction <= 0 \
                or player2 + player2_size*1.05 > SCREEN_HEIGHT \
                or player2 - player2_size*1.05 > 0:
                    reaction = random.randint(2, 5)
                    if error is None:
                        error = random.randint(
                            int(-player2_size),
                            int(player2_size)
                        )
                    direction = 0
                    if bally + error < player2_paddle - player2_size/4:
                        direction -= 1
                    if bally + error > player2_paddle + player2_size/4:
                        direction += 1
                    player2_speed = direction*speed

            # temporary variable storing ratio
            ratio = (
                balls / (
                    (SCREEN_WIDTH + SCREEN_WIDTH)/2*0.005
                ) * 25
            )

            # temp variables
            tspeed1 = player1_speed
            player1_speed = max(min(player1_speed, speed), -speed)
            tpoints = points
            tballs = balls
            tpaddle = 0

            # move in little steps for precise collision detection
            for i in range(int(ratio)):
                # check if paddle is safe to be moved
                tpaddle = max(tpaddle - 1, 0)
                try:
                    if tpaddle > 0:
                        raise UnboundLocalError
                    p1_side
                    if not any((
                        p1_side, p2_side,
                        p1_cap, p2_cap,
                    )):
                        tpaddle = 4
                        raise UnboundLocalError
                except UnboundLocalError:
                    # update paddle positions
                    player1_paddle += player1_speed/ratio
                    player2_paddle += player2_speed/ratio

                    # restrict paddle location
                    if player1_paddle - player1_size < 0 \
                    or player1_paddle + player1_size \
                    > SCREEN_HEIGHT + 1:
                        player1_paddle -= player1_speed/ratio
                    if player2_paddle - player2_size < 0 \
                    or player2_paddle + player2_size \
                    > SCREEN_HEIGHT + 1:
                        player2_paddle -= player2_speed/ratio
                else:
                    # reverse paddle positions
                    player1_paddle -= player1_speed/ratio*4
                    player2_paddle -= player2_speed/ratio*4

                    # restrict paddle location
                    if player1_paddle - player1_size < 0 \
                    or player1_paddle + player1_size \
                    > SCREEN_HEIGHT + 1:
                        player1_paddle += player1_speed/ratio*4
                    if player2_paddle - player2_size < 0 \
                    or player2_paddle + player2_size \
                    > SCREEN_HEIGHT + 1:
                        player2_paddle += player2_speed/ratio*4

                # check if ball is supposed to move
                if delay <= 0:
                    # reset delay
                    delay = 0

                    # set temp speed
                    balln = balld

                    # get where collision is happening
                    p1_side = \
                        ballx - ballr <= SCREEN_WIDTH*0.06 \
                        and ballx - ballr/4 >= SCREEN_WIDTH*0.06 \
                        and player1_paddle - player1_size - ballr \
                        <= bally \
                        <= player1_paddle + player1_size + ballr
                    p2_side = \
                        ballx + ballr >= SCREEN_WIDTH*0.94 \
                        and ballx + ballr/4 <= SCREEN_WIDTH*0.94 \
                        and player2_paddle - player2_size - ballr \
                        <= bally \
                        <= player2_paddle + player2_size + ballr
                    p1_loss = ballx + ballr < 0
                    p2_loss = ballx - ballr > SCREEN_WIDTH

                    # undo move if needed
                    if p1_side or p2_side:
                        ballx -= m.cos(m.radians(balld))*balls*2.5/ratio

                    # get where collision is happening
                    top_bottom = \
                        bally - ballr < 0 \
                        or bally + ballr > SCREEN_HEIGHT + 1
                    p1_cap = \
                        ballx - ballr < SCREEN_WIDTH*0.06 \
                        and ballx + ballr > SCREEN_WIDTH*0.05 \
                        and bally - ballr \
                        <= player1_paddle + player1_size \
                        and bally + ballr \
                        >= player1_paddle - player1_size
                    p2_cap = \
                        ballx - ballr > SCREEN_WIDTH*0.94 \
                        and ballx + ballr < SCREEN_WIDTH*0.95 \
                        and bally - ballr \
                        <= player2_paddle + player2_size \
                        and bally + ballr \
                        >= player2_paddle - player2_size

                    # undo move if needed
                    if p1_cap or p2_cap:
                        bally -= -m.sin(m.radians(balld))*balls*2.5/ratio
                    if top_bottom:
                        bally -= -m.sin(m.radians(balld))*balls*2.5/ratio

                    # extra stuff to change direction
                    if p1_loss or p2_loss:
                        if p1_loss:
                            player2 += points
                        elif p2_loss:
                            player1 += points
                        matches += 1
                        points = 0
                        ballx = SCREEN_WIDTH/2
                        bally = SCREEN_HEIGHT/2
                        balld = random.randint(1, 360)
                        balls = (SCREEN_WIDTH + SCREEN_WIDTH)/2*0.005
                        delay = 60
                        while 75 < balld < 105 or 255 < balld < 285:
                            balld = random.randint(1, 360)
                        balln = balld
                        break
                    elif any((
                        p1_cap, p2_cap,
                        p1_side, p2_side,
                        top_bottom,
                    )):
                        if p1_cap or p2_cap:
                            balln = balln*-1
                        elif p1_side or p2_side:
                            balln = balln*-1 + 180
                            balls += 0.2
                            points += 1
                        if top_bottom:
                            balln = balln*-1
                        break

                    # change location
                    ballx += m.cos(m.radians(balld))*balls*1.25/ratio
                    bally += -m.sin(m.radians(balld))*balls*1.25/ratio

                    # check everything after ball moved
                    # temp speed variable
                    if balld != balln:
                        balld = balln + 180

                    # get where collision is happening
                    p1_side = \
                        ballx - ballr <= SCREEN_WIDTH*0.06 \
                        and ballx - ballr/4 >= SCREEN_WIDTH*0.06 \
                        and player1_paddle - player1_size - ballr \
                        <= bally \
                        <= player1_paddle + player1_size + ballr
                    p2_side = \
                        ballx + ballr >= SCREEN_WIDTH*0.94 \
                        and ballx + ballr/4 <= SCREEN_WIDTH*0.94 \
                        and player2_paddle - player2_size - ballr \
                        <= bally \
                        <= player2_paddle + player2_size + ballr
                    p1_loss = ballx + ballr < 0
                    p2_loss = ballx - ballr > SCREEN_WIDTH

                    # undo move if needed
                    if p1_side or p2_side:
                        ballx -= m.cos(m.radians(balld))*balls*2.5/ratio

                    # get where collision is happening
                    top_bottom = \
                        bally - ballr < 0 \
                        or bally + ballr > SCREEN_HEIGHT + 1
                    p1_cap = \
                        ballx - ballr < SCREEN_WIDTH*0.06 \
                        and ballx + ballr > SCREEN_WIDTH*0.05 \
                        and bally - ballr \
                        <= player1_paddle + player1_size \
                        and bally + ballr \
                        >= player1_paddle - player1_size
                    p2_cap = \
                        ballx + ballr > SCREEN_WIDTH*0.94 \
                        and ballx - ballr < SCREEN_WIDTH*0.95 \
                        and bally - ballr \
                        <= player2_paddle + player2_size \
                        and bally + ballr \
                        >= player2_paddle - player2_size

                    # undo move if needed
                    if p1_cap or p2_cap:
                        bally -= -m.sin(m.radians(balld))*balls*2.5/ratio
                    if top_bottom:
                        bally -= -m.sin(m.radians(balld))*balls*2.5/ratio

                    # temp speed variable
                    balld = balln

                    # extra stuff to change direction
                    if p1_loss or p2_loss:
                        if p1_loss:
                            player2 += points
                        elif p2_loss:
                            player1 += points
                        matches += 1
                        points = 0
                        ballx = SCREEN_WIDTH/2
                        bally = SCREEN_HEIGHT/2
                        balld = random.randint(1, 360)
                        balls = (SCREEN_WIDTH + SCREEN_WIDTH)/2*0.005
                        delay = 60
                        while 75 < balld < 105 or 255 < balld < 285:
                            balld = random.randint(1, 360)
                        balln = balld
                        break
                    elif any((
                        p1_cap, p2_cap,
                        p1_side, p2_side,
                        top_bottom,
                    )):
                        if p1_cap or p2_cap:
                            balln = balln*-1
                        elif p1_side or p2_side:
                            balln = balln*-1 + 180
                            balls += 0.2
                            points += 1
                        if top_bottom:
                            balln = balln*-1
                        break

                    # set new ball direction
                    balld = balln
            # end for

            # set new ball direction and speed
            balld = balln
            balls = min(tballs + 0.2, balls)

            # set new points
            points = min(points, tpoints + 1)

            # reset player speed
            player1_speed = tspeed1

        # draw things
        pygame.draw.rect(
            screen, BUTTON,
            (
                SCREEN_WIDTH*0.05, player1_paddle - player1_size,
                SCREEN_WIDTH*0.01, player1_size*2
            )
        )
        pygame.draw.rect(
            screen, BUTTON,
            (
                SCREEN_WIDTH*0.94, player2_paddle - player2_size,
                SCREEN_WIDTH*0.01, player2_size*2
            )
        )
        pygame.draw.rect(
            screen, BUTTON,
            (
                int(ballx - ballr), int(bally - ballr),
                int(ballr*2), int(ballr*2)
            )
        )
        draw_text(
            screen,
            SCREEN_WIDTH*0.5,
            SCREEN_HEIGHT*0.1,
            str(points),
            size = 50
        )
        draw_text(
            screen,
            SCREEN_WIDTH*0.2,
            SCREEN_HEIGHT*0.1,
            str(player1),
            size = 30
        )
        draw_text(
            screen,
            SCREEN_WIDTH*0.8,
            SCREEN_HEIGHT*0.1,
            str(player2),
            size = 30
        )

        # paused menu
        if paused:
            pygame.draw.rect(
                screen, BUTTON,
                (
                    SCREEN_WIDTH*0.2, SCREEN_HEIGHT*0.1,
                    SCREEN_WIDTH*0.6, SCREEN_HEIGHT*0.2
                )
            )
            draw_text(
                screen,
                SCREEN_WIDTH*0.5,
                SCREEN_HEIGHT*0.21,
                'MENU',
                size = 90
            )
            pygame.draw.rect(
                screen, BUTTON,
                (
                    SCREEN_WIDTH*0.35, SCREEN_HEIGHT*0.45,
                    SCREEN_WIDTH*0.3, SCREEN_HEIGHT*0.1
                )
            )
            draw_text(
                screen,
                SCREEN_WIDTH*0.5,
                SCREEN_HEIGHT*0.505,
                'RESUME',
                size = 30
            )
            pygame.draw.rect(
                screen, BUTTON,
                (
                    SCREEN_WIDTH*0.35, SCREEN_HEIGHT*0.6,
                    SCREEN_WIDTH*0.3, SCREEN_HEIGHT*0.1
                )
            )
            draw_text(
                screen,
                SCREEN_WIDTH*0.5,
                SCREEN_HEIGHT*0.655,
                'MAIN MENU',
                size = 30
            )

        # update screen
        pygame.display.update()
        clock.tick(60) # 60 fps
    # end while

    # check if force exited
    if matches == 21:
        return None, [0, '']

    # screen time
    delay = 180

    # get winner string
    if player1 == player2:
        winner = 'Tie Game!'
    elif max(player1, player2) == player1:
        if not ai:
            winner = 'Player 1 Won!'
        else:
            winner = 'Player Won!'
    elif not ai:
        winner = 'Player 2 Won!'
    else:
        winner = 'Artificial Intelligence Won!'

    # end screen
    while delay > 0:
        # default screen background
        screen.fill(BACKGROUND)

        # event checking
        for event in pygame.event.get():
            if event.type == QUIT:
                delay = 200
                break
        # end for

        if delay == 200:
            break

        # draw winner text
        draw_text(
            screen,
            SCREEN_WIDTH/2,
            SCREEN_HEIGHT/2,
            winner,
            size = 70,
        )
        draw_text(
            screen,
            SCREEN_WIDTH/2,
            SCREEN_HEIGHT*0.7,
            str(max(player1, player2)),
            size = 40,
        )

        # update screen
        delay -= 1
        pygame.display.update()
        clock.tick(60) # 60 fps
    # end while

    # return high score
    return max(player1, player2), [0, '']
# end local

# online multiplayer code
def online(screen):
    # colours
    SCREEN_WIDTH = 800 # width of window
    SCREEN_HEIGHT = 600 # height of window
    WHITE = (255, 255, 255)
    RED = (255, 0, 0)
    BLACK = (0, 0, 0)
    BUTTON = (166, 200, 100)
    BACKGROUND = (124, 124, 180)

    # game variables
    clock = pygame.time.Clock() # make screen clock
    matches = 0

    # online variables
    ip = socket.gethostbyname(socket.gethostname())
    if ip == '127.0.0.1':
        return None, [180, 'Not connected to internet', 40]
    other = ''
    error = None
    current = None
    reader = None
    writer = None
    info = []
    receive = []
    '''
format for info

0 server x
1 server y
2 ball x
3 ball y
4 client x
5 client y
6 server points
7 client points
8 ball points (negative: delay, positive: bounces)
9 matches

format for receive

0 client direction
'''

    # loop
    while True:
        # clear screen
        screen.fill(BACKGROUND)

        # make buttons
        def draw_button(x, y, w, h, text, size=50, **kwargs):
            pygame.draw.rect(
                screen, BUTTON,
                (
                    SCREEN_WIDTH*x, SCREEN_HEIGHT*y,
                    SCREEN_WIDTH*w, SCREEN_HEIGHT*h
                )
            )
            draw_text(
                screen,
                SCREEN_WIDTH*(x + w/2),
                SCREEN_HEIGHT*(y + h/2 + 0.005),
                text,
                size=50,
                **kwargs
            )
        # end draw_button
        draw_button(0.3, 0.4, 0.4, 0.1, other)
        draw_button(0.3, 0.55, 0.4, 0.1, 'JOIN')
        draw_button(0.3, 0.7, 0.4, 0.1, 'CREATE')
        draw_button(0.3, 0.85, 0.4, 0.1, 'MENU')
        draw_text(
            screen,
            SCREEN_WIDTH*0.5,
            SCREEN_HEIGHT*0.15,
            'Online Pong',
            size = 120
        )
        draw_text(
            screen,
            SCREEN_WIDTH*0.5,
            SCREEN_HEIGHT*0.3,
            f'IP: {ip}',
            size = 50
        )

        # update display
        pygame.display.update()

        # event checking
        for event in pygame.event.get():
            if event.type == MOUSEBUTTONDOWN:
                x, y = event.pos
                if SCREEN_WIDTH*0.3 < x < SCREEN_WIDTH*0.7:
                    if SCREEN_HEIGHT*0.4 < y < SCREEN_HEIGHT*0.5:
                        current = 'input'
                    elif SCREEN_HEIGHT*0.55 < y < SCREEN_HEIGHT*0.65:
                        current = 'join'
                        try:
                            async def test_join():
                                reader, writer = \
                                await asyncio.open_connection(
                                    other, 41001
                                )
                                writer.write('test join\n'.encode())
                                await writer.drain()
                                data = await reader.readline()
                                data = data.decode().rstrip()
                                if data == 'accepted':
                                    writer.close()
                                else:
                                    raise OSError(
                                        'Server already connected'
                                    )
                            # end test_join
                            asyncio.run(test_join())
                        except OSError as e:
                            current = 'menu'
                            error = [180, str(e), int(1100/len(str(e)))]
                        else:
                            current = 'client'
                    elif SCREEN_HEIGHT*0.7 < y < SCREEN_HEIGHT*0.8:
                        current = 'server'
                    elif SCREEN_HEIGHT*0.85 < y < SCREEN_HEIGHT*0.95:
                        current = 'menu'
                        break
            elif event.type == KEYDOWN:
                if current == 'input':
                    if event.unicode in tuple('0123456789.'):
                        other = other + event.unicode
                    elif event.key == K_BACKSPACE:
                        other = other[:-1]
            elif event.type == QUIT:
                current = 'menu'
                break
        # end for

        # check if needed to exit loop
        if current in (
            'menu',
            'server',
            'client',
        ):
            break

        clock.tick(60)
    # end while

    # check if exiting to menu
    if current == 'menu':
        if error is None:
            error = [0, '']
        return None, error

    # continue to server / client / asyncio / socket madness
    # beware guys, this is some hardcore f***.
    # \x0bjg!uifsf(t!tujmm!fsspst!jo!uijt!qbsu-!qmfbtf!lffq!jo!njoe!uibu\
    # x0buijt!uijoh!uppl!vq!bspvoe!1/111:669512946324263!pg!nz!mjgf/\x0bo
    # px-!uibu!njhiu!tffn!mjlf!b!mpu-!cvu!uiptf!xfsf!b!gvmm!6!ebzt\x0buib
    # u!j!dpvme(wf!tqfou!epjoh!puifs!uijoht!tvdi!bt!gjoejoh!b\x0bdvuf!hjs
    # mgsjfoe!)zfbi!op*!ps!nbzcf!kvtu!qsbdujtjoh!npsf!wjpmjo/\x0bzfbi!xib
    # u!ibt!uijt!cfdpnf///\x0bjg!ns/!bouipoz-!zpv(sf!tffjoh!uijt-!j!kvtu!
    # xbou!up!tbz///\x0buibol!zpv/!uibol!zpv!gps!ufbdijoh!bmm!pg!vt!bcpvu
    # !dpnqvufst!boe\x0bibsexbsf!boe!uifjs!jnqbdu!po!tpdjfuz-!bt!xjuipvu!
    # pvs!bnb{joh\x0bufbdifs-!xf!njhiu(wf!ofwfs!mfbsofe!xibu!fggfdu!dpnqv
    # ufst\x0bhjwf!jo!pvs!mjwft/!cfdbvtf!pg!zpv-!j(wf!opx!mfbsou!fopvhi!u
    # p\x0bnbzcf!nblf!b!npcjmf!bqq!boe!tubsu!fbsojoh!tpnf!npofz!up!tbwf\x
    # 0bvq!gps!vojwfstjuz/!uibol!zpv!;E\x0b
    # print(''.join(chr(ord(i) - 1) for i in text)
    if current == 'server':
        async def server_screen():
            nonlocal matches
            nonlocal info
            nonlocal receive
            points = 0
            player1 = 0
            player2 = 0
            player1_paddle = SCREEN_HEIGHT*0.5
            player2_paddle = SCREEN_HEIGHT*0.5
            player1_speed = 0
            player2_speed = 0
            player1_size = SCREEN_HEIGHT*0.075
            player2_size = SCREEN_HEIGHT*0.075
            speed = (SCREEN_WIDTH + SCREEN_WIDTH)/2*0.005
            balls = (SCREEN_WIDTH + SCREEN_WIDTH)/2*0.005
            ballx = SCREEN_WIDTH/2
            bally = SCREEN_HEIGHT/2
            ballr = (SCREEN_WIDTH + SCREEN_WIDTH)/2*0.01
            balld = random.randint(1, 360)
            delay = 60
            while 75 < balld < 105 or 255 < balld < 285:
                balld = random.randint(1, 360)
            balln = balld
            info = [
                0, player1_paddle,
                ballx, bally,
                0, player2_paddle,
                player1,
                player2,
                points if delay <= 0 else -delay,
                matches,
                player1_speed,
            ]

            # loop
            while matches < 10:
                # default screen background
                screen.fill(BACKGROUND)

                # process info
                try:
                    player2_speed = receive[0]
                    player2_paddle = info[5]
                    player1 = int(info[6])
                    player2 = int(info[7])
                    if info[8] < 0:
                        delay = -info[8]
                    else:
                        points = info[8]
                except IndexError:
                    draw_text(
                        screen,
                        SCREEN_WIDTH*0.5,
                        SCREEN_HEIGHT*0.15,
                        'Waiting for other...',
                        size = 80
                    )
                    draw_text(
                        screen,
                        SCREEN_WIDTH*0.5,
                        SCREEN_HEIGHT*0.3,
                        f'IP: {ip}',
                        size = 50
                    )
                    for event in pygame.event.get():
                        if event.type == QUIT:
                            matches = 21
                            break
                    # end for
                    pygame.display.update()
                    await asyncio.sleep(0.015)
                    continue

                # event checking
                for event in pygame.event.get():
                    if event.type == KEYDOWN:
                        if event.key == K_w:
                            player1_speed += -speed
                        elif event.key == K_s:
                            player1_speed += speed
                        elif event.key == K_UP:
                            player1_speed += -speed
                        elif event.key == K_DOWN:
                            player1_speed += speed
                    elif event.type == KEYUP:
                        if event.key == K_w:
                            player1_speed -= -speed
                        elif event.key == K_s:
                            player1_speed -= speed
                        elif event.key == K_UP:
                            player1_speed -= -speed
                        elif event.key == K_DOWN:
                            player1_speed -= speed
                    elif event.type == QUIT:
                        matches = 21
                        break
                # end for

                # break loop if quit
                if matches == 21:
                    break

                # update server speed
                info[10] = player1_speed

                # decrement delay
                delay = max(delay - 1, 0)

                # temporary variable storing ratio
                ratio = (
                    balls / (
                        (SCREEN_WIDTH + SCREEN_WIDTH)/2*0.005
                    ) * 25
                )

                # temp variables
                tpoints = points
                tballs = balls
                tpaddle = 0
                tspeed1 = player1_speed
                tspeed2 = player2_speed
                player1_speed = min(max(player1_speed, -speed), speed)
                player2_speed = min(max(player2_speed, -speed), speed)

                # move in little steps for precise collision detection
                for i in range(int(ratio)):
                    # check if paddle is safe to be moved
                    tpaddle = max(tpaddle - 1, 0)
                    try:
                        if tpaddle > 0:
                            raise UnboundLocalError
                        p1_side
                        if not any((
                            p1_side, p2_side,
                            p1_cap, p2_cap,
                        )):
                            tpaddle = 4
                            raise UnboundLocalError
                    except UnboundLocalError:
                        # update paddle positions
                        player1_paddle += player1_speed/ratio
                        player2_paddle += player2_speed/ratio

                        # restrict paddle location
                        if player1_paddle - player1_size < 0 \
                        or player1_paddle + player1_size \
                        > SCREEN_HEIGHT + 1:
                            player1_paddle -= player1_speed/ratio
                        if player2_paddle - player2_size < 0 \
                        or player2_paddle + player2_size \
                        > SCREEN_HEIGHT + 1:
                            player2_paddle -= player2_speed/ratio
                    else:
                        # reverse paddle positions
                        player1_paddle -= player1_speed/ratio*4
                        player2_paddle -= player2_speed/ratio*4

                        # restrict paddle location
                        if player1_paddle - player1_size < 0 \
                        or player1_paddle + player1_size \
                        > SCREEN_HEIGHT + 1:
                            player1_paddle += player1_speed/ratio*4
                        if player2_paddle - player2_size < 0 \
                        or player2_paddle + player2_size \
                        > SCREEN_HEIGHT + 1:
                            player2_paddle += player2_speed/ratio*4

                    # check if ball is supposed to move
                    if delay <= 0:
                        # reset delay
                        delay = 0

                        # set temp speed
                        balln = balld

                        # get where collision is happening
                        p1_side = \
                            ballx - ballr <= SCREEN_WIDTH*0.06 \
                            and ballx - ballr/4 >= SCREEN_WIDTH*0.06 \
                            and player1_paddle - player1_size - ballr \
                            <= bally \
                            <= player1_paddle + player1_size + ballr
                        p2_side = \
                            ballx + ballr >= SCREEN_WIDTH*0.94 \
                            and ballx + ballr/4 <= SCREEN_WIDTH*0.94 \
                            and player2_paddle - player2_size - ballr \
                            <= bally \
                            <= player2_paddle + player2_size + ballr
                        p1_loss = ballx + ballr < 0
                        p2_loss = ballx - ballr > SCREEN_WIDTH

                        # undo move if needed
                        if p1_side or p2_side:
                            ballx -= m.cos(m.radians(balld)) \
                                *balls*2.5/ratio

                        # get where collision is happening
                        top_bottom = \
                            bally - ballr < 0 \
                            or bally + ballr > SCREEN_HEIGHT + 1
                        p1_cap = \
                            ballx - ballr < SCREEN_WIDTH*0.06 \
                            and ballx + ballr > SCREEN_WIDTH*0.05 \
                            and bally - ballr \
                            <= player1_paddle + player1_size \
                            and bally + ballr \
                            >= player1_paddle - player1_size
                        p2_cap = \
                            ballx - ballr > SCREEN_WIDTH*0.94 \
                            and ballx + ballr < SCREEN_WIDTH*0.95 \
                            and bally - ballr \
                            <= player2_paddle + player2_size \
                            and bally + ballr \
                            >= player2_paddle - player2_size

                        # undo move if needed
                        if p1_cap or p2_cap:
                            bally -= -m.sin(m.radians(balld)) \
                                *balls*2.5/ratio
                        if top_bottom:
                            bally -= -m.sin(m.radians(balld)) \
                                *balls*2.5/ratio

                        # extra stuff to change direction
                        if p1_loss or p2_loss:
                            if p1_loss:
                                player2 += points
                            elif p2_loss:
                                player1 += points
                            matches += 1
                            points = 0
                            ballx = SCREEN_WIDTH/2
                            bally = SCREEN_HEIGHT/2
                            balld = random.randint(1, 360)
                            balls = (SCREEN_WIDTH + SCREEN_WIDTH)/2*0.005
                            delay = 60
                            while 75 < balld < 105 or 255 < balld < 285:
                                balld = random.randint(1, 360)
                            balln = balld
                            break
                        elif any((
                            p1_cap, p2_cap,
                            p1_side, p2_side,
                            top_bottom,
                        )):
                            if p1_cap or p2_cap:
                                balln = balln*-1
                            elif p1_side or p2_side:
                                balln = balln*-1 + 180
                                balls += 0.2
                                points += 1
                            if top_bottom:
                                balln = balln*-1
                            break

                        # change location
                        ballx += m.cos(m.radians(balld))*balls*1.25/ratio
                        bally += -m.sin(m.radians(balld))*balls*1.25/ratio

                        # check everything after ball moved
                        # temp speed variable
                        if balld != balln:
                            balld = balln + 180

                        # get where collision is happening
                        p1_side = \
                            ballx - ballr <= SCREEN_WIDTH*0.06 \
                            and ballx - ballr/4 >= SCREEN_WIDTH*0.06 \
                            and player1_paddle - player1_size - ballr \
                            <= bally \
                            <= player1_paddle + player1_size + ballr
                        p2_side = \
                            ballx + ballr >= SCREEN_WIDTH*0.94 \
                            and ballx + ballr/4 <= SCREEN_WIDTH*0.94 \
                            and player2_paddle - player2_size - ballr \
                            <= bally \
                            <= player2_paddle + player2_size + ballr
                        p1_loss = ballx + ballr < 0
                        p2_loss = ballx - ballr > SCREEN_WIDTH

                        # undo move if needed
                        if p1_side or p2_side:
                            ballx -= m.cos(m.radians(balld)) \
                                *balls*2.5/ratio

                        # get where collision is happening
                        top_bottom = \
                            bally - ballr < 0 \
                            or bally + ballr > SCREEN_HEIGHT + 1
                        p1_cap = \
                            ballx - ballr < SCREEN_WIDTH*0.06 \
                            and ballx + ballr > SCREEN_WIDTH*0.05 \
                            and bally - ballr \
                            <= player1_paddle + player1_size \
                            and bally + ballr \
                            >= player1_paddle - player1_size
                        p2_cap = \
                            ballx + ballr > SCREEN_WIDTH*0.94 \
                            and ballx - ballr < SCREEN_WIDTH*0.95 \
                            and bally - ballr \
                            <= player2_paddle + player2_size \
                            and bally + ballr \
                            >= player2_paddle - player2_size

                        # undo move if needed
                        if p1_cap or p2_cap:
                            bally -= -m.sin(m.radians(balld)) \
                                *balls*2.5/ratio
                        if top_bottom:
                            bally -= -m.sin(m.radians(balld)) \
                                *balls*2.5/ratio

                        # temp speed variable
                        balld = balln

                        # extra stuff to change direction
                        if p1_loss or p2_loss:
                            if p1_loss:
                                player2 += points
                            elif p2_loss:
                                player1 += points
                            matches += 1
                            points = 0
                            ballx = SCREEN_WIDTH/2
                            bally = SCREEN_HEIGHT/2
                            balld = random.randint(1, 360)
                            balls = (SCREEN_WIDTH + SCREEN_WIDTH)/2*0.005
                            delay = 60
                            while 75 < balld < 105 or 255 < balld < 285:
                                balld = random.randint(1, 360)
                            balln = balld
                            break
                        elif any((
                            p1_cap, p2_cap,
                            p1_side, p2_side,
                            top_bottom,
                        )):
                            if p1_cap or p2_cap:
                                balln = balln*-1
                            elif p1_side or p2_side:
                                balln = balln*-1 + 180
                                balls += 0.2
                                points += 1
                            if top_bottom:
                                balln = balln*-1
                            break

                        # set new ball direction
                        balld = balln
                # end for

                # set new ball direction and speed
                balld = balln
                balls = min(tballs + 0.2, balls)

                # set new points
                points = min(points, tpoints + 1)

                # reset speed
                player1_speed = tspeed1
                player2_speed = tspeed2

                # update info to send
                info[1] = player1_paddle
                info[2] = ballx
                info[3] = bally
                info[5] = player2_paddle
                info[6] = player1
                info[7] = player2
                if delay > 0:
                    info[8] = -delay
                else:
                    info[8] = points
                info[9] = matches

                # draw things
                pygame.draw.rect(
                    screen, BUTTON,
                    (
                        SCREEN_WIDTH*0.05, player1_paddle - player1_size,
                        SCREEN_WIDTH*0.01, player1_size*2
                    )
                )
                pygame.draw.rect(
                    screen, BUTTON,
                    (
                        SCREEN_WIDTH*0.94, player2_paddle - player2_size,
                        SCREEN_WIDTH*0.01, player2_size*2
                    )
                )
                pygame.draw.rect(
                    screen, BUTTON,
                    (
                        int(ballx - ballr), int(bally - ballr),
                        int(ballr*2), int(ballr*2)
                    )
                )
                draw_text(
                    screen,
                    SCREEN_WIDTH*0.5,
                    SCREEN_HEIGHT*0.1,
                    str(points),
                    size = 50
                )
                draw_text(
                    screen,
                    SCREEN_WIDTH*0.2,
                    SCREEN_HEIGHT*0.1,
                    str(player1),
                    size = 30
                )
                draw_text(
                    screen,
                    SCREEN_WIDTH*0.8,
                    SCREEN_HEIGHT*0.1,
                    str(player2),
                    size = 30
                )

                # update screen
                pygame.display.update()
                await asyncio.sleep(0.03) # clock.tick(60) # 60 fps
            # end while

            # check if force exited
            if matches == 21:
                return

            # screen time
            delay = 180

            # get winner string
            if player1 == player2:
                winner = 'Tie Game!'
            elif max(player1, player2) == player1:
                winner = 'You Won!'
            else:
                winner = 'Client Won!'

            # end screen
            while delay > 0:
                # default screen background
                screen.fill(BACKGROUND)

                # event checking
                for event in pygame.event.get():
                    if event.type == QUIT:
                        delay = 200
                        break
                # end for

                if delay == 200:
                    break

                # draw winner text
                draw_text(
                    screen,
                    SCREEN_WIDTH/2,
                    SCREEN_HEIGHT/2,
                    winner,
                    size = 70,
                )
                draw_text(
                    screen,
                    SCREEN_WIDTH/2,
                    SCREEN_HEIGHT*0.7,
                    str(max(player1, player2)),
                    size = 40,
                )

                # update screen
                delay -= 1
                pygame.display.update()
                await asyncio.sleep(0.015) # clock.tick(60) # 60 fps
            # end while
        # end server_screen()
        async def handle_request(reader, writer):
            nonlocal other
            nonlocal matches
            nonlocal info
            nonlocal receive
            nonlocal error
            data = await reader.readline()
            data = data.decode().rstrip()
            addr = writer.get_extra_info('peername')
            if not other and data == 'test join':
                other = (addr[0],)
                writer.write('accepted\n'.encode())
            elif addr[0] == other[0]:
                if len(other) == 1:
                    other = other[0], addr[1]
                if data == 'disconnected':
                    matches = 21
                    error = [180, 'Client closed unexpectedly.', 35]
                else:
                    receive = [float(i) for i in data.split()]
                    writer.write((
                        ' '.join(str(i) for i in info) + '\n'
                        ).encode()
                    )
                    try:
                        await writer.drain()
                    except ConnectionError as e:
                        error = [180, str(e), int(1100/len(str(e)))]
                    else:
                        while matches < 10:
                            try:
                                data = await asyncio.wait_for(
                                    reader.readline(), 1
                                )
                                data = data.decode().rstrip()
                                if not data or data == 'disconnected':
                                    matches = 21
                                    error = [
                                        180,
                                        'Client closed unexpectedly.',
                                        35,
                                    ]
                                    break
                            except ConnectionError as e:
                                if matches >= 10:
                                    break
                                matches = 21
                                error = [
                                    180, str(e),
                                    int(1100/len(str(e))),
                                ]
                                writer.close()
                                return
                            except Exception as e:
                                if matches >= 10:
                                    break
                                matches = 21
                                if len(str(e)) != 0:
                                    error = [
                                        180, str(e),
                                        int(1100/len(str(e))),
                                    ]
                                else:
                                    error = [
                                        180,
                                        'Client closed unexpectedly.',
                                        35,
                                    ]
                                writer.close()
                                return
                            else:
                                receive = [float(i) for i in data.split()]
                                writer.write((
                                    ' '.join(str(i) for i in info) + '\n'
                                    ).encode()
                                )
                                try:
                                    await writer.drain()
                                except ConnectionError as e:
                                    if matches >= 10:
                                        break
                                    matches = 21
                                    error = [
                                        180, str(e),
                                        int(1100/len(str(e))),
                                    ]
                                    writer.close()
                                    return
                        # end while
            else:
                writer.write('denied\n'.encode())
            try:
                await writer.drain()
            except ConnectionError:
                pass
            writer.close()
        # end handle_request
        async def make_server():
            nonlocal matches
            nonlocal error
            try:
                server = await asyncio.start_server(
                    handle_request, ip, 41001,
                )
            except OSError as e:
                error = [180, str(e), int(1100/len(str(e)))]
                matches = 21
                server.close()
                await server.wait_closed()
                return
            while matches < 10:
                await asyncio.sleep(0.5)
            # end while
            if matches >= 10:
                if matches == 21:
                    error = [180, 'Client closed unexpectedly.', 35]
                server.close()
                await server.wait_closed()
        # end make_server
        async def server_side():
            await asyncio.gather(
                make_server(),
                server_screen(),
            )
        # end server_side()
        asyncio.run(server_side())
    elif current == 'client':
        receive = [0]
        async def client_screen():
            nonlocal matches
            nonlocal info
            nonlocal receive
            points = 0
            player1 = 0
            player2 = 0
            player1_paddle = SCREEN_HEIGHT*0.5
            player2_paddle = SCREEN_HEIGHT*0.5
            player1_speed = 0
            player2_speed = 0
            player1_size = SCREEN_HEIGHT*0.075
            player2_size = SCREEN_HEIGHT*0.075
            speed = (SCREEN_WIDTH + SCREEN_WIDTH)/2*0.005
            balls = 0
            ballx = SCREEN_WIDTH/2
            bally = SCREEN_HEIGHT/2
            ballr = (SCREEN_WIDTH + SCREEN_WIDTH)/2*0.01
            balld = 0
            delay = 60
            while 75 < balld < 105 or 255 < balld < 285:
                balld = random.randint(1, 360)
            balln = balld
            info = [
                0, player1_paddle,
                ballx, bally,
                0, player2_paddle,
                player1,
                player2,
                points if delay <= 0 else -delay,
                matches,
                player1_speed,
            ]

            # loop
            while matches < 10:
                # default screen background
                screen.fill(BACKGROUND)

                # process info
                try:
                    player1_paddle = info[1]
                    ballx = info[2]
                    bally = info[3]
                    player2_paddle = info[5]
                    player1 = int(info[6])
                    player2 = int(info[7])
                    if info[8] < 0:
                        delay = int(-info[8])
                    else:
                        points = int(info[8])
                    matches = int(info[9])
                    player1_speed = info[10]
                except IndexError:
                    draw_text(
                        screen,
                        SCREEN_WIDTH*0.5,
                        SCREEN_HEIGHT*0.15,
                        'Waiting for other...',
                        size = 80
                    )
                    draw_text(
                        screen,
                        SCREEN_WIDTH*0.5,
                        SCREEN_HEIGHT*0.3,
                        f'IP: {ip}',
                        size = 50
                    )
                    for event in pygame.event.get():
                        if event.type == QUIT:
                            matches = 21
                            break
                    # end for
                    pygame.display.update()
                    await asyncio.sleep(0.015)
                    continue

                # event checking
                for event in pygame.event.get():
                    if event.type == KEYDOWN:
                        if event.key == K_w:
                            player2_speed += -speed
                        elif event.key == K_s:
                            player2_speed += speed
                        elif event.key == K_UP:
                            player2_speed += -speed
                        elif event.key == K_DOWN:
                            player2_speed += speed
                    elif event.type == KEYUP:
                        if event.key == K_w:
                            player2_speed -= -speed
                        elif event.key == K_s:
                            player2_speed -= speed
                        elif event.key == K_UP:
                            player2_speed -= -speed
                        elif event.key == K_DOWN:
                            player2_speed -= speed
                    elif event.type == QUIT:
                        matches = 21
                        break
                # end for

                # break loop if quit
                if matches == 21:
                    break

                # update info to send
                try:
                    receive[0] = player2_speed
                except IndexError:
                    receive = [player2_speed]

                # decrement delay
                delay = max(delay - 1, 0)

                # temporary variable storing ratio
                ratio = (
                    balls / (
                        (SCREEN_WIDTH + SCREEN_WIDTH)/2*0.005
                    ) * 25
                )

                # temp variables
                tpoints = points
                tballs = balls
                tpaddle = 0
                tspeed1 = player1_speed
                tspeed2 = player2_speed
                player1_speed = min(max(player1_speed, -speed), speed)
                player2_speed = min(max(player2_speed, -speed), speed)

                # move in little steps for precise collision detection
                for i in range(int(ratio)):
                    # check if paddle is safe to be moved
                    tpaddle = max(tpaddle - 1, 0)
                    try:
                        if tpaddle > 0:
                            raise UnboundLocalError
                        p1_side
                        if not any((
                            p1_side, p2_side,
                            p1_cap, p2_cap,
                        )):
                            tpaddle = 4
                            raise UnboundLocalError
                    except UnboundLocalError:
                        # update paddle positions
                        player1_paddle += player1_speed/ratio
                        player2_paddle += player2_speed/ratio

                        # restrict paddle location
                        if player1_paddle - player1_size < 0 \
                        or player1_paddle + player1_size \
                        > SCREEN_HEIGHT + 1:
                            player1_paddle -= player1_speed/ratio
                        if player2_paddle - player2_size < 0 \
                        or player2_paddle + player2_size \
                        > SCREEN_HEIGHT + 1:
                            player2_paddle -= player2_speed/ratio
                    else:
                        # reverse paddle positions
                        player1_paddle -= player1_speed/ratio*4
                        player2_paddle -= player2_speed/ratio*4

                        # restrict paddle location
                        if player1_paddle - player1_size < 0 \
                        or player1_paddle + player1_size \
                        > SCREEN_HEIGHT + 1:
                            player1_paddle += player1_speed/ratio*4
                        if player2_paddle - player2_size < 0 \
                        or player2_paddle + player2_size \
                        > SCREEN_HEIGHT + 1:
                            player2_paddle += player2_speed/ratio*4

                    # check if ball is supposed to move
                    if delay <= 0:
                        # reset delay
                        delay = 0

                        # set temp speed
                        balln = balld

                        # get where collision is happening
                        p1_side = \
                            ballx - ballr <= SCREEN_WIDTH*0.06 \
                            and ballx - ballr/4 >= SCREEN_WIDTH*0.06 \
                            and player1_paddle - player1_size - ballr \
                            <= bally \
                            <= player1_paddle + player1_size + ballr
                        p2_side = \
                            ballx + ballr >= SCREEN_WIDTH*0.94 \
                            and ballx + ballr/4 <= SCREEN_WIDTH*0.94 \
                            and player2_paddle - player2_size - ballr \
                            <= bally \
                            <= player2_paddle + player2_size + ballr
                        p1_loss = ballx + ballr < 0
                        p2_loss = ballx - ballr > SCREEN_WIDTH

                        # undo move if needed
                        if p1_side or p2_side:
                            ballx -= m.cos(m.radians(balld)) \
                                *balls*2.5/ratio

                        # get where collision is happening
                        top_bottom = \
                            bally - ballr < 0 \
                            or bally + ballr > SCREEN_HEIGHT + 1
                        p1_cap = \
                            ballx - ballr < SCREEN_WIDTH*0.06 \
                            and ballx + ballr > SCREEN_WIDTH*0.05 \
                            and bally - ballr \
                            <= player1_paddle + player1_size \
                            and bally + ballr \
                            >= player1_paddle - player1_size
                        p2_cap = \
                            ballx - ballr > SCREEN_WIDTH*0.94 \
                            and ballx + ballr < SCREEN_WIDTH*0.95 \
                            and bally - ballr \
                            <= player2_paddle + player2_size \
                            and bally + ballr \
                            >= player2_paddle - player2_size

                        # undo move if needed
                        if p1_cap or p2_cap:
                            bally -= -m.sin(m.radians(balld)) \
                                *balls*2.5/ratio
                        if top_bottom:
                            bally -= -m.sin(m.radians(balld)) \
                                *balls*2.5/ratio

                        # extra stuff to change direction
                        if p1_loss or p2_loss:
                            if p1_loss:
                                player2 += points
                            elif p2_loss:
                                player1 += points
                            matches += 1
                            points = 0
                            ballx = SCREEN_WIDTH/2
                            bally = SCREEN_HEIGHT/2
                            balld = random.randint(1, 360)
                            balls = (SCREEN_WIDTH + SCREEN_WIDTH)/2*0.005
                            delay = 60
                            while 75 < balld < 105 or 255 < balld < 285:
                                balld = random.randint(1, 360)
                            balln = balld
                            break
                        elif any((
                            p1_cap, p2_cap,
                            p1_side, p2_side,
                            top_bottom,
                        )):
                            if p1_cap or p2_cap:
                                balln = balln*-1
                            elif p1_side or p2_side:
                                balln = balln*-1 + 180
                                balls += 0.2
                                points += 1
                            if top_bottom:
                                balln = balln*-1
                            break

                        # change location
                        ballx += m.cos(m.radians(balld))*balls*1.25/ratio
                        bally += -m.sin(m.radians(balld))*balls*1.25/ratio

                        # check everything after ball moved
                        # temp speed variable
                        if balld != balln:
                            balld = balln + 180

                        # get where collision is happening
                        p1_side = \
                            ballx - ballr <= SCREEN_WIDTH*0.06 \
                            and ballx - ballr/4 >= SCREEN_WIDTH*0.06 \
                            and player1_paddle - player1_size - ballr \
                            <= bally \
                            <= player1_paddle + player1_size + ballr
                        p2_side = \
                            ballx + ballr >= SCREEN_WIDTH*0.94 \
                            and ballx + ballr/4 <= SCREEN_WIDTH*0.94 \
                            and player2_paddle - player2_size - ballr \
                            <= bally \
                            <= player2_paddle + player2_size + ballr
                        p1_loss = ballx + ballr < 0
                        p2_loss = ballx - ballr > SCREEN_WIDTH

                        # undo move if needed
                        if p1_side or p2_side:
                            ballx -= m.cos(m.radians(balld)) \
                                *balls*2.5/ratio

                        # get where collision is happening
                        top_bottom = \
                            bally - ballr < 0 \
                            or bally + ballr > SCREEN_HEIGHT + 1
                        p1_cap = \
                            ballx - ballr < SCREEN_WIDTH*0.06 \
                            and ballx + ballr > SCREEN_WIDTH*0.05 \
                            and bally - ballr \
                            <= player1_paddle + player1_size \
                            and bally + ballr \
                            >= player1_paddle - player1_size
                        p2_cap = \
                            ballx + ballr > SCREEN_WIDTH*0.94 \
                            and ballx - ballr < SCREEN_WIDTH*0.95 \
                            and bally - ballr \
                            <= player2_paddle + player2_size \
                            and bally + ballr \
                            >= player2_paddle - player2_size

                        # undo move if needed
                        if p1_cap or p2_cap:
                            bally -= -m.sin(m.radians(balld)) \
                                *balls*2.5/ratio
                        if top_bottom:
                            bally -= -m.sin(m.radians(balld)) \
                                *balls*2.5/ratio

                        # temp speed variable
                        balld = balln

                        # extra stuff to change direction
                        if p1_loss or p2_loss:
                            if p1_loss:
                                player2 += points
                            elif p2_loss:
                                player1 += points
                            matches += 1
                            points = 0
                            ballx = SCREEN_WIDTH/2
                            bally = SCREEN_HEIGHT/2
                            balld = random.randint(1, 360)
                            balls = (SCREEN_WIDTH + SCREEN_WIDTH)/2*0.005
                            delay = 60
                            while 75 < balld < 105 or 255 < balld < 285:
                                balld = random.randint(1, 360)
                            balln = balld
                            break
                        elif any((
                            p1_cap, p2_cap,
                            p1_side, p2_side,
                            top_bottom,
                        )):
                            if p1_cap or p2_cap:
                                balln = balln*-1
                            elif p1_side or p2_side:
                                balln = balln*-1 + 180
                                balls += 0.2
                                points += 1
                            if top_bottom:
                                balln = balln*-1
                            break

                        # set new ball direction
                        balld = balln
                # end for

                # set new ball direction and speed
                balld = balln
                balls = min(tballs + 0.2, balls)

                # set new points
                points = min(points, tpoints + 1)

                # reset speed
                player1_speed = tspeed1
                player2_speed = tspeed2

                # draw things
                pygame.draw.rect(
                    screen, BUTTON,
                    (
                        SCREEN_WIDTH*0.05, player1_paddle - player1_size,
                        SCREEN_WIDTH*0.01, player1_size*2
                    )
                )
                pygame.draw.rect(
                    screen, BUTTON,
                    (
                        SCREEN_WIDTH*0.94, player2_paddle - player2_size,
                        SCREEN_WIDTH*0.01, player2_size*2
                    )
                )
                pygame.draw.rect(
                    screen, BUTTON,
                    (
                        int(ballx - ballr), int(bally - ballr),
                        int(ballr*2), int(ballr*2)
                    )
                )
                draw_text(
                    screen,
                    SCREEN_WIDTH*0.5,
                    SCREEN_HEIGHT*0.1,
                    str(points),
                    size = 50
                )
                draw_text(
                    screen,
                    SCREEN_WIDTH*0.2,
                    SCREEN_HEIGHT*0.1,
                    str(player1),
                    size = 30
                )
                draw_text(
                    screen,
                    SCREEN_WIDTH*0.8,
                    SCREEN_HEIGHT*0.1,
                    str(player2),
                    size = 30
                )

                # update screen
                pygame.display.update()
                await asyncio.sleep(0.03) # clock.tick(60) # 60 fps
            # end while

            # check if force exited
            if matches == 21:
                return

            # screen time
            delay = 180

            # get winner string
            if player1 == player2:
                winner = 'Tie Game!'
            elif max(player1, player2) == player1:
                winner = 'Host Won!'
            else:
                winner = 'You Won!'

            # end screen
            while delay > 0:
                # default screen background
                screen.fill(BACKGROUND)

                # event checking
                for event in pygame.event.get():
                    if event.type == QUIT:
                        delay = 200
                        break
                # end for

                if delay == 200:
                    break

                # draw winner text
                draw_text(
                    screen,
                    SCREEN_WIDTH/2,
                    SCREEN_HEIGHT/2,
                    winner,
                    size = 70,
                )
                draw_text(
                    screen,
                    SCREEN_WIDTH/2,
                    SCREEN_HEIGHT*0.7,
                    str(max(player1, player2)),
                    size = 40,
                )

                # update screen
                delay -= 1
                pygame.display.update()
                await asyncio.sleep(0.015) # clock.tick(60) # 60 fps
            # end while
        # end client_screen
        async def start_request():
            nonlocal other
            nonlocal matches
            nonlocal info
            nonlocal receive
            nonlocal error
            reader, writer = await asyncio.open_connection(
                other, 41001
            )
            while matches < 10:
                writer.write((
                    ' '.join(str(r) for r in receive) + '\n'
                    ).encode()
                )
                try:
                    await writer.drain()
                except ConnectionError as e:
                    if matches >= 10:
                        break
                    matches = 21
                    error = [180, str(e), int(1100/len(str(e)))]
                    break
                while True:
                    try:
                        data = await asyncio.wait_for(
                            reader.readline(), 1
                        )
                        data = data.decode().rstrip()
                        if not data and matches < 10:
                            matches = 21
                        break
                    except Exception:
                        matches = 21
                        break
                # end while
                if matches == 21:
                    error = [180, 'Host closed unexpectedly.', 35]
                    break
                elif data == 'disconnected':
                    matches = 21
                    error = [180, 'Host closed unexpectedly.', 35]
                    break
                else:
                    info_ = [float(i) for i in data.split()]
                    info = info_
                    matches = info[9]
            # end while
            try:
                writer.write('disconnected\n'.encode())
                await writer.drain()
            except ConnectionError:
                pass
            writer.close()
        # end handle_request
        async def make_client():
            await start_request()
        # end make_server
        async def client_side():
            await asyncio.gather(
                make_client(),
                client_screen(),
            )
        # end server_side()
        asyncio.run(client_side())
    if error is None:
        error = [0, '']
    return None, error
# end online

if __name__ == '__main__':
    main()
