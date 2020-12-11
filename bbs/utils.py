"""
# coding:utf-8
@Time    : 2020/12/02
@Author  : jiangwei
@mail    : jiangwei1@kylinos.cn
@File    : utils.py
@Software: PyCharm
"""
import re
from markdown import extensions
from markdown.treeprocessors import Treeprocessor

try:
    from urlparse import urlparse, urljoin
except ImportError:
    from urllib.parse import urlparse, urljoin

from flask import request, url_for, redirect

EMOJI_INFOS = [
    [('older-man_1f474.png', 'older-man'), ('face-with-look-of-triumph_1f624.png', 'face-with-look-of-triumph'),
     ('man_1f468.png', 'man'), ('prince_1f934.png', 'prince'), ('loudly-crying-face_1f62d.png', 'loudly-crying-face'), (
     'smiling-face-with-open-mouth-and-tightly-closed-eyes_1f606.png',
     'smiling-face-with-open-mouth-and-tightly-closed-eyes'),
     ('woman-running_1f3c3-200d-2640-fe0f.png', 'woman-running'),
     ('happy-person-raising-one-hand_1f64b.png', 'happy-person-raising-one-hand')],
    [('female-student_1f469-200d-1f393.png', 'female-student'),
     ('family-woman-woman-girl-girl_1f469-200d-1f469-200d-1f467-200d-1f467.png', 'family-woman-woman-girl-girl'),
     ('man-pouting_1f64e-200d-2642-fe0f.png', 'man-pouting'), ('sparkling-heart_1f496.png', 'sparkling-heart'),
     ('woman-climbing_1f9d7-200d-2640-fe0f.png', 'woman-climbing'),
     ('serious-face-with-symbols-covering-mouth_1f92c.png', 'serious-face-with-symbols-covering-mouth'),
     ('female-scientist_1f469-200d-1f52c.png', 'female-scientist'), ('family_1f46a.png', 'family')],
    [('fearful-face_1f628.png', 'fearful-face'), ('selfie_1f933.png', 'selfie'),
     ('extraterrestrial-alien_1f47d.png', 'extraterrestrial-alien'), ('neutral-face_1f610.png', 'neutral-face'),
     ('grinning-face-with-star-eyes_1f929.png', 'grinning-face-with-star-eyes'),
     ('family-man-woman-girl_1f468-200d-1f469-200d-1f467.png', 'family-man-woman-girl'),
     ('family-woman-girl_1f469-200d-1f467.png', 'family-woman-girl'), ('japanese-dolls_1f38e.png', 'japanese-dolls')],
    [('merwoman_1f9dc-200d-2640-fe0f.png', 'merwoman'), ('haircut_1f487.png', 'haircut'),
     ('man-vampire_1f9db-200d-2642-fe0f.png', 'man-vampire'), ('genie_1f9de.png', 'genie'),
     ('smiling-face-with-horns_1f608.png', 'smiling-face-with-horns'),
     ('face-with-stuck-out-tongue-and-winking-eye_1f61c.png', 'face-with-stuck-out-tongue-and-winking-eye'),
     ('male-astronaut_1f468-200d-1f680.png', 'male-astronaut'),
     ('busts-in-silhouette_1f465.png', 'busts-in-silhouette')],
    [('woman-with-bunny-ears_1f46f.png', 'woman-with-bunny-ears'),
     ('face-savouring-delicious-food_1f60b.png', 'face-savouring-delicious-food'),
     ('family-woman-woman-boy_1f469-200d-1f469-200d-1f466.png', 'family-woman-woman-boy'),
     ('expressionless-face_1f611.png', 'expressionless-face'), ('white-smiling-face_263a.png', 'white-smiling-face'),
     ('male-police-officer_1f46e-200d-2642-fe0f.png', 'male-police-officer'),
     ('disappointed-face_1f61e.png', 'disappointed-face'),
     ('family-woman-boy-boy_1f469-200d-1f466-200d-1f466.png', 'family-woman-boy-boy')],
    [('male-factory-worker_1f468-200d-1f3ed.png', 'male-factory-worker'),
     ('face-with-open-mouth_1f62e.png', 'face-with-open-mouth'),
     ('man-shrugging_1f937-200d-2642-fe0f.png', 'man-shrugging'),
     ('woman-tipping-hand_1f481-200d-2640-fe0f.png', 'woman-tipping-hand'), ('elf_1f9dd.png', 'elf'),
     ('couple-with-heart_1f491.png', 'couple-with-heart'), ('woman-mage_1f9d9-200d-2640-fe0f.png', 'woman-mage'),
     ('disappointed-but-relieved-face_1f625.png', 'disappointed-but-relieved-face')],
    [('persevering-face_1f623.png', 'persevering-face'),
     ('male-technologist_1f468-200d-1f4bb.png', 'male-technologist'),
     ('female-singer_1f469-200d-1f3a4.png', 'female-singer'), ('male-scientist_1f468-200d-1f52c.png', 'male-scientist'),
     ('frowning-face-with-open-mouth_1f626.png', 'frowning-face-with-open-mouth'),
     ('man-running_1f3c3-200d-2642-fe0f.png', 'man-running'), ('mage_1f9d9.png', 'mage'),
     ('female-health-worker_1f469-200d-2695-fe0f.png', 'female-health-worker')],
    [('female-astronaut_1f469-200d-1f680.png', 'female-astronaut'), ('sleuth-or-spy_1f575.png', 'sleuth-or-spy'),
     ('woman-shrugging_1f937-200d-2640-fe0f.png', 'woman-shrugging'),
     ('family-woman-woman-girl-boy_1f469-200d-1f469-200d-1f467-200d-1f466.png', 'family-woman-woman-girl-boy'),
     ('father-christmas_1f385.png', 'father-christmas'), ('woman-genie_1f9de-200d-2640-fe0f.png', 'woman-genie'),
     ('zipper-mouth-face_1f910.png', 'zipper-mouth-face'), ('face-with-ok-gesture_1f646.png', 'face-with-ok-gesture')],
    [('face-with-medical-mask_1f637.png', 'face-with-medical-mask'),
     ('kiss-man-man_1f468-200d-2764-fe0f-200d-1f48b-200d-1f468.png', 'kiss-man-man'), ('kiss_1f48f.png', 'kiss'),
     ('smiling-face-with-open-mouth_1f603.png', 'smiling-face-with-open-mouth'),
     ('pregnant-woman_1f930.png', 'pregnant-woman'), ('face-with-monocle_1f9d0.png', 'face-with-monocle'),
     ('female-police-officer_1f46e-200d-2640-fe0f.png', 'female-police-officer'),
     ('pouting-face_1f621.png', 'pouting-face')],
    [('man-in-tuxedo_1f935.png', 'man-in-tuxedo'), ('pensive-face_1f614.png', 'pensive-face'),
     ('fairy_1f9da.png', 'fairy'), ('male-judge_1f468-200d-2696-fe0f.png', 'male-judge'),
     ('male-singer_1f468-200d-1f3a4.png', 'male-singer'),
     ('man-raising-hand_1f64b-200d-2642-fe0f.png', 'man-raising-hand'), (
     'face-with-stuck-out-tongue-and-tightly-closed-eyes_1f61d.png',
     'face-with-stuck-out-tongue-and-tightly-closed-eyes'), ('drooling-face_1f924.png', 'drooling-face')],
    [('runner_1f3c3.png', 'runner'), ('kissing-face-with-closed-eyes_1f61a.png', 'kissing-face-with-closed-eyes'),
     ('male-cook_1f468-200d-1f373.png', 'male-cook'),
     ('smiling-face-with-sunglasses_1f60e.png', 'smiling-face-with-sunglasses'),
     ('face-with-stuck-out-tongue_1f61b.png', 'face-with-stuck-out-tongue'), ('face-massage_1f486.png', 'face-massage'),
     ('female-sleuth_1f575-fe0f-200d-2640-fe0f.png', 'female-sleuth'), ('beating-heart_1f493.png', 'beating-heart')],
    [('tired-face_1f62b.png', 'tired-face'), ('woman-vampire_1f9db-200d-2640-fe0f.png', 'woman-vampire'),
     ('see-no-evil-monkey_1f648.png', 'see-no-evil-monkey'), ('kissing-face_1f617.png', 'kissing-face'),
     ('shrug_1f937.png', 'shrug'), ('male-office-worker_1f468-200d-1f4bc.png', 'male-office-worker'),
     ('man-climbing_1f9d7-200d-2642-fe0f.png', 'man-climbing'), ('relieved-face_1f60c.png', 'relieved-face')],
    [('family-woman-girl-boy_1f469-200d-1f467-200d-1f466.png', 'family-woman-girl-boy'),
     ('male-teacher_1f468-200d-1f3eb.png', 'male-teacher'),
     ('woman-in-lotus-position_1f9d8-200d-2640-fe0f.png', 'woman-in-lotus-position'),
     ('mother-christmas_1f936.png', 'mother-christmas'),
     ('smiling-face-with-heart-shaped-eyes_1f60d.png', 'smiling-face-with-heart-shaped-eyes'),
     ('breast-feeding_1f931.png', 'breast-feeding'),
     ('man-in-steamy-room_1f9d6-200d-2642-fe0f.png', 'man-in-steamy-room'), (
     'smiling-face-with-smiling-eyes-and-hand-covering-mouth_1f92d.png',
     'smiling-face-with-smiling-eyes-and-hand-covering-mouth')],
    [('man-elf_1f9dd-200d-2642-fe0f.png', 'man-elf'), ('confused-face_1f615.png', 'confused-face'),
     ('woman_1f469.png', 'woman'), ('female-office-worker_1f469-200d-1f4bc.png', 'female-office-worker'),
     ('woman-zombie_1f9df-200d-2640-fe0f.png', 'woman-zombie'),
     ('smiling-face-with-smiling-eyes_1f60a.png', 'smiling-face-with-smiling-eyes'),
     ('woman-wearing-turban_1f473-200d-2640-fe0f.png', 'woman-wearing-turban'),
     ('woman-bowing-deeply_1f647-200d-2640-fe0f.png', 'woman-bowing-deeply')],
    [('tongue_1f445.png', 'tongue'), ('man-getting-haircut_1f487-200d-2642-fe0f.png', 'man-getting-haircut'),
     ('man-facepalming_1f926-200d-2642-fe0f.png', 'man-facepalming'), ('nauseated-face_1f922.png', 'nauseated-face'),
     ('sleepy-face_1f62a.png', 'sleepy-face'), ('face-screaming-in-fear_1f631.png', 'face-screaming-in-fear'),
     ('face-with-open-mouth-vomiting_1f92e.png', 'face-with-open-mouth-vomiting'),
     ('smirking-face_1f60f.png', 'smirking-face')],
    [('astonished-face_1f632.png', 'astonished-face'), ('purple-heart_1f49c.png', 'purple-heart'),
     ('slightly-frowning-face_1f641.png', 'slightly-frowning-face'), ('grinning-face_1f600.png', 'grinning-face'),
     ('woman-elf_1f9dd-200d-2640-fe0f.png', 'woman-elf'),
     ('female-factory-worker_1f469-200d-1f3ed.png', 'female-factory-worker'),
     ('bride-with-veil_1f470.png', 'bride-with-veil'),
     ('smiling-face-with-open-mouth-and-smiling-eyes_1f604.png', 'smiling-face-with-open-mouth-and-smiling-eyes')],
    [('woman-raising-hand_1f64b-200d-2640-fe0f.png', 'woman-raising-hand'), ('mouth_1f444.png', 'mouth'),
     ('baby-angel_1f47c.png', 'baby-angel'), ('vampire_1f9db.png', 'vampire'),
     ('smiling-face-with-halo_1f607.png', 'smiling-face-with-halo'),
     ('rolling-on-the-floor-laughing_1f923.png', 'rolling-on-the-floor-laughing'),
     ('female-pilot_1f469-200d-2708-fe0f.png', 'female-pilot'),
     ('female-artist_1f469-200d-1f3a8.png', 'female-artist')],
    [('older-woman_1f475.png', 'older-woman'), ('revolving-hearts_1f49e.png', 'revolving-hearts'),
     ('male-farmer_1f468-200d-1f33e.png', 'male-farmer'), ('female-teacher_1f469-200d-1f3eb.png', 'female-teacher'),
     ('male-guard_1f482-200d-2642-fe0f.png', 'male-guard'), ('man-with-turban_1f473.png', 'man-with-turban'),
     ('lying-face_1f925.png', 'lying-face'), ('merman_1f9dc-200d-2642-fe0f.png', 'merman')],
    [('smiling-face-with-open-mouth-and-cold-sweat_1f605.png', 'smiling-face-with-open-mouth-and-cold-sweat'),
     ('child_1f9d2.png', 'child'), ('growing-heart_1f497.png', 'growing-heart'), ('kiss-mark_1f48b.png', 'kiss-mark'),
     ('heart-with-arrow_1f498.png', 'heart-with-arrow'), ('sneezing-face_1f927.png', 'sneezing-face'),
     ('family-man-man-girl-boy_1f468-200d-1f468-200d-1f467-200d-1f466.png', 'family-man-man-girl-boy'),
     ('slightly-smiling-face_1f642.png', 'slightly-smiling-face')],
    [('woman-gesturing-not-ok_1f645-200d-2640-fe0f.png', 'woman-gesturing-not-ok'),
     ('family-man-man-boy-boy_1f468-200d-1f468-200d-1f466-200d-1f466.png', 'family-man-man-boy-boy'),
     ('family-man-woman-boy-boy_1f468-200d-1f469-200d-1f466-200d-1f466.png', 'family-man-woman-boy-boy'),
     ('man-walking_1f6b6-200d-2642-fe0f.png', 'man-walking'),
     ('family-man-girl-girl_1f468-200d-1f467-200d-1f467.png', 'family-man-girl-girl'),
     ('man-getting-face-massage_1f486-200d-2642-fe0f.png', 'man-getting-face-massage'),
     ('green-heart_1f49a.png', 'green-heart'),
     ('female-construction-worker_1f477-200d-2640-fe0f.png', 'female-construction-worker')],
    [('person-climbing_1f9d7.png', 'person-climbing'), ('hushed-face_1f62f.png', 'hushed-face'),
     ('grinning-face-with-one-large-and-one-small-eye_1f92a.png', 'grinning-face-with-one-large-and-one-small-eye'),
     ('face-without-mouth_1f636.png', 'face-without-mouth'),
     ('family-man-man-girl_1f468-200d-1f468-200d-1f467.png', 'family-man-man-girl'),
     ('speak-no-evil-monkey_1f64a.png', 'speak-no-evil-monkey'), ('guardsman_1f482.png', 'guardsman'),
     ('weary-face_1f629.png', 'weary-face')], [('female-firefighter_1f469-200d-1f692.png', 'female-firefighter'), (
    'family-man-man-girl-girl_1f468-200d-1f468-200d-1f467-200d-1f467.png', 'family-man-man-girl-girl'),
                                               ('face-with-head-bandage_1f915.png', 'face-with-head-bandage'),
                                               ('man-gesturing-ok_1f646-200d-2642-fe0f.png', 'man-gesturing-ok'),
                                               ('imp_1f47f.png', 'imp'),
                                               ('construction-worker_1f477.png', 'construction-worker'),
                                               ('broken-heart_1f494.png', 'broken-heart'), (
                                               'face-with-finger-covering-closed-lips_1f92b.png',
                                               'face-with-finger-covering-closed-lips')],
    [('japanese-ogre_1f479.png', 'japanese-ogre'),
     ('man-in-business-suit-levitating_1f574.png', 'man-in-business-suit-levitating'),
     ('nerd-face_1f913.png', 'nerd-face'), ('anguished-face_1f627.png', 'anguished-face'),
     ('female-guard_1f482-200d-2640-fe0f.png', 'female-guard'), ('merperson_1f9dc.png', 'merperson'),
     ('man-mage_1f9d9-200d-2642-fe0f.png', 'man-mage'),
     ('woman-gesturing-ok_1f646-200d-2640-fe0f.png', 'woman-gesturing-ok')],
    [('man-fairy_1f9da-200d-2642-fe0f.png', 'man-fairy'),
     ('women-with-bunny-ears-partying_1f46f-200d-2640-fe0f.png', 'women-with-bunny-ears-partying'),
     ('sleeping-face_1f634.png', 'sleeping-face'), ('face-with-thermometer_1f912.png', 'face-with-thermometer'),
     ('male-health-worker_1f468-200d-2695-fe0f.png', 'male-health-worker'),
     ('family-man-woman-girl-boy_1f468-200d-1f469-200d-1f467-200d-1f466.png', 'family-man-woman-girl-boy'),
     ('face-throwing-a-kiss_1f618.png', 'face-throwing-a-kiss'), ('dancer_1f483.png', 'dancer')],
    [('hear-no-evil-monkey_1f649.png', 'hear-no-evil-monkey'), ('clown-face_1f921.png', 'clown-face'),
     ('face-with-open-mouth-and-cold-sweat_1f630.png', 'face-with-open-mouth-and-cold-sweat'),
     ('woman-pouting_1f64e-200d-2640-fe0f.png', 'woman-pouting'), ('two-hearts_1f495.png', 'two-hearts'),
     ('man-wearing-turban_1f473-200d-2642-fe0f.png', 'man-wearing-turban'),
     ('person-with-pouting-face_1f64e.png', 'person-with-pouting-face'),
     ('face-with-no-good-gesture_1f645.png', 'face-with-no-good-gesture')],
    [('police-officer_1f46e.png', 'police-officer'),
     ('woman-in-steamy-room_1f9d6-200d-2640-fe0f.png', 'woman-in-steamy-room'),
     ('upside-down-face_1f643.png', 'upside-down-face'),
     ('family-man-man-boy_1f468-200d-1f468-200d-1f466.png', 'family-man-man-boy'),
     ('couple-with-heart-man-man_1f468-200d-2764-fe0f-200d-1f468.png', 'couple-with-heart-man-man'),
     ('shocked-face-with-exploding-head_1f92f.png', 'shocked-face-with-exploding-head'), ('girl_1f467.png', 'girl'),
     ('woman-getting-face-massage_1f486-200d-2640-fe0f.png', 'woman-getting-face-massage')],
    [('family-man-girl-boy_1f468-200d-1f467-200d-1f466.png', 'family-man-girl-boy'),
     ('kiss-woman-woman_1f469-200d-2764-fe0f-200d-1f48b-200d-1f469.png', 'kiss-woman-woman'),
     ('man-bowing-deeply_1f647-200d-2642-fe0f.png', 'man-bowing-deeply'),
     ('family-woman-woman-boy-boy_1f469-200d-1f469-200d-1f466-200d-1f466.png', 'family-woman-woman-boy-boy'),
     ('snowman-without-snow_26c4.png', 'snowman-without-snow'),
     ('kissing-face-with-smiling-eyes_1f619.png', 'kissing-face-with-smiling-eyes'),
     ('woman-frowning_1f64d-200d-2640-fe0f.png', 'woman-frowning'),
     ('face-with-cold-sweat_1f613.png', 'face-with-cold-sweat')],
    [('yellow-heart_1f49b.png', 'yellow-heart'), ('speech-balloon_1f4ac.png', 'speech-balloon'),
     ('blue-heart_1f499.png', 'blue-heart'), ('japanese-goblin_1f47a.png', 'japanese-goblin'),
     ('nose_1f443.png', 'nose'), ('family-woman-woman-girl_1f469-200d-1f469-200d-1f467.png', 'family-woman-woman-girl'),
     ('confounded-face_1f616.png', 'confounded-face'), ('angry-face_1f620.png', 'angry-face')],
    [('snowman_2603.png', 'snowman'), ('zombie_1f9df.png', 'zombie'), ('moyai_1f5ff.png', 'moyai'),
     ('face-with-rolling-eyes_1f644.png', 'face-with-rolling-eyes'),
     ('female-farmer_1f469-200d-1f33e.png', 'female-farmer'), ('unamused-face_1f612.png', 'unamused-face'),
     ('skull-and-crossbones_2620.png', 'skull-and-crossbones'),
     ('female-technologist_1f469-200d-1f4bb.png', 'female-technologist')],
    [('bust-in-silhouette_1f464.png', 'bust-in-silhouette'), ('baby_1f476.png', 'baby'),
     ('person-in-lotus-position_1f9d8.png', 'person-in-lotus-position'),
     ('woman-walking_1f6b6-200d-2640-fe0f.png', 'woman-walking'),
     ('information-desk-person_1f481.png', 'information-desk-person'),
     ('male-sleuth_1f575-fe0f-200d-2642-fe0f.png', 'male-sleuth'), ('hugging-face_1f917.png', 'hugging-face'),
     ('female-judge_1f469-200d-2696-fe0f.png', 'female-judge')],
    [('man-gesturing-not-ok_1f645-200d-2642-fe0f.png', 'man-gesturing-not-ok'),
     ('female-mechanic_1f469-200d-1f527.png', 'female-mechanic'), ('worried-face_1f61f.png', 'worried-face'),
     ('orange-heart_1f9e1.png', 'orange-heart'), ('grimacing-face_1f62c.png', 'grimacing-face'),
     ('male-firefighter_1f468-200d-1f692.png', 'male-firefighter'),
     ('family-man-boy_1f468-200d-1f466.png', 'family-man-boy'), ('man-dancing_1f57a.png', 'man-dancing')],
    [('face-with-tears-of-joy_1f602.png', 'face-with-tears-of-joy'),
     ('man-frowning_1f64d-200d-2642-fe0f.png', 'man-frowning'), ('ghost_1f47b.png', 'ghost'),
     ('male-pilot_1f468-200d-2708-fe0f.png', 'male-pilot'), ('pedestrian_1f6b6.png', 'pedestrian'),
     ('boy_1f466.png', 'boy'), ('grinning-face-with-smiling-eyes_1f601.png', 'grinning-face-with-smiling-eyes'),
     ('dizzy-face_1f635.png', 'dizzy-face')],
    [('heavy-black-heart_2764.png', 'heavy-black-heart'), ('princess_1f478.png', 'princess'),
     ('woman-fairy_1f9da-200d-2640-fe0f.png', 'woman-fairy'),
     ('person-in-steamy-room_1f9d6.png', 'person-in-steamy-room'),
     ('male-student_1f468-200d-1f393.png', 'male-student'), ('face-palm_1f926.png', 'face-palm'),
     ('black-heart_1f5a4.png', 'black-heart'), ('skull_1f480.png', 'skull')],
    [('family-man-woman-girl-girl_1f468-200d-1f469-200d-1f467-200d-1f467.png', 'family-man-woman-girl-girl'),
     ('male-construction-worker_1f477-200d-2642-fe0f.png', 'male-construction-worker'),
     ('male-mechanic_1f468-200d-1f527.png', 'male-mechanic'),
     ('woman-getting-haircut_1f487-200d-2640-fe0f.png', 'woman-getting-haircut'),
     ('men-with-bunny-ears-partying_1f46f-200d-2642-fe0f.png', 'men-with-bunny-ears-partying'),
     ('female-cook_1f469-200d-1f373.png', 'female-cook'), ('face-with-cowboy-hat_1f920.png', 'face-with-cowboy-hat'),
     ('money-mouth-face_1f911.png', 'money-mouth-face')],
    [('crying-face_1f622.png', 'crying-face'), ('wind-blowing-face_1f32c.png', 'wind-blowing-face'),
     ('face-with-one-eyebrow-raised_1f928.png', 'face-with-one-eyebrow-raised'),
     ('flushed-face_1f633.png', 'flushed-face'), ('family-man-girl_1f468-200d-1f467.png', 'family-man-girl'),
     ('couple-with-heart-woman-woman_1f469-200d-2764-fe0f-200d-1f469.png', 'couple-with-heart-woman-woman'),
     ('heart-with-ribbon_1f49d.png', 'heart-with-ribbon'), ('person-bowing-deeply_1f647.png', 'person-bowing-deeply')],
    [('man-in-lotus-position_1f9d8-200d-2642-fe0f.png', 'man-in-lotus-position'),
     ('male-artist_1f468-200d-1f3a8.png', 'male-artist'), ('person-frowning_1f64d.png', 'person-frowning'),
     ('love-letter_1f48c.png', 'love-letter'), ('woman-facepalming_1f926-200d-2640-fe0f.png', 'woman-facepalming'),
     ('thinking-face_1f914.png', 'thinking-face'), ('white-frowning-face_2639.png', 'white-frowning-face'),
     ('person-with-headscarf_1f9d5.png', 'person-with-headscarf')],
    [('man-tipping-hand_1f481-200d-2642-fe0f.png', 'man-tipping-hand'), ('winking-face_1f609.png', 'winking-face')]]


def get_emoji_url():
    """
    获取所有表情的url连接
    :return: 所有表情的url链接
    """
    emoji_urls = []
    url = '/static/emojis/{}'
    tmp = []
    for emoji in EMOJI_INFOS:
        for e in emoji:
            tmp.append(url.format(e[0]))
        emoji_urls.append(tmp)
    return emoji_urls


def validate_username(username):
    r = re.match('^[a-zA-Z0-9_]*$', username)
    return True if r else False


def is_safe_url(target):
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and ref_url.netloc == test_url.netloc


def redirect_back(default='index_bp.index', **kwargs):
    for target in request.args.get('next'), request.referrer:
        if not target:
            continue
        if is_safe_url(target):
            return redirect(target)
    return redirect(url_for(default, **kwargs))


def get_text_plain(html_text):
    from bs4 import BeautifulSoup
    bs = BeautifulSoup(html_text, 'html.parser')
    return bs.get_text()


class MyMDStyleTreeProcessor(Treeprocessor):
    def run(self, root):
        for child in root.getiterator():
            if child.tag == 'table':
                child.set("class", "table table-bordered table-hover")
            elif child.tag == 'img':
                child.set("class", "d-block img-fluid mx-auto")
            elif child.tag == 'blockquote':
                child.set('class', 'blockquote-comment')
            elif child.tag == 'p':
                child.set('class', 'mt-0 mb-0 p-break')
            elif child.tag == 'pre':
                child.set('class', 'mb-0')
            elif child.tag == 'h1':
                child.set('class', 'comment-h1')
            elif child.tag == 'h2':
                child.set('class', 'comment-h2')
            elif child.tag == 'h3':
                child.set('class', 'comment-h3')
            elif child.tag in ['h4', 'h5', 'h6']:
                child.set('class', 'comment-h4')
        return root


# noinspection PyAttributeOutsideInit
class MyMDStyleExtension(extensions.Extension):
    def extendMarkdown(self, md):
        md.registerExtension(self)
        self.processor = MyMDStyleTreeProcessor()
        self.processor.md = md
        self.processor.config = self.getConfigs()
        md.treeprocessors.add('mystyle', self.processor, '_end')
