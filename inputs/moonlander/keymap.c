#include QMK_KEYBOARD_H
#include "version.h"
#define MOON_LED_LEVEL LED_LEVEL
#ifndef ZSA_SAFE_RANGE
#define ZSA_SAFE_RANGE SAFE_RANGE
#endif

enum custom_keycodes {
  RGB_SLD = ZSA_SAFE_RANGE,
};



enum tap_dance_codes {
  DANCE_0,
};


const uint16_t PROGMEM keymaps[][MATRIX_ROWS][MATRIX_COLS] = {
  [0] = LAYOUT_moonlander(
    KC_GRAVE,       KC_1,           KC_2,           KC_3,           KC_4,           KC_5,           RGB_MODE_FORWARD,                                TD(DANCE_0),    KC_6,           KC_7,           KC_8,           KC_9,           KC_0,           KC_MINUS,       
    LT(3, KC_TAB),  KC_Q,           KC_W,           KC_E,           KC_R,           KC_T,           KC_TRANSPARENT,                                 KC_MINUS,       KC_Y,           KC_U,           KC_I,           KC_O,           KC_P,           KC_BSLS,        
    KC_LEFT_CTRL,   KC_A,           KC_S,           KC_D,           KC_F,           KC_G,           KC_LBRC,                                                                        KC_RBRC,        KC_H,           KC_J,           KC_K,           KC_L,           KC_SCLN,        KC_QUOTE,       
    SC_LSPO,        KC_Z,           KC_X,           KC_C,           KC_V,           KC_B,                                           KC_N,           KC_M,           KC_COMMA,       KC_DOT,         KC_SLASH,       SC_RSPC,        
    MO(3),          CW_TOGG,        KC_TRANSPARENT, KC_LEFT_ALT,    KC_LEFT_GUI,    KC_TRANSPARENT,                                                                                                 KC_TRANSPARENT, MO(4),          KC_LEFT,        KC_DOWN,        KC_UP,          KC_RIGHT,       
    KC_ENTER,       KC_ESCAPE,      KC_TRANSPARENT,                 KC_TRANSPARENT, KC_BSPC,        KC_SPACE
  ),
  [1] = LAYOUT_moonlander(
    KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT,                                 KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_EQUAL,       
    KC_TRANSPARENT, KC_QUOTE,       KC_COMMA,       KC_DOT,         KC_P,           KC_Y,           KC_TRANSPARENT,                                 KC_BSLS,        KC_F,           KC_G,           KC_C,           KC_R,           KC_L,           KC_SLASH,       
    KC_TRANSPARENT, KC_A,           KC_O,           KC_E,           KC_U,           KC_I,           KC_TRANSPARENT,                                                                 KC_TRANSPARENT, KC_D,           KC_H,           KC_T,           KC_N,           KC_S,           KC_MINUS,       
    KC_TRANSPARENT, KC_SCLN,        KC_Q,           KC_J,           KC_K,           KC_X,                                           KC_B,           KC_M,           KC_W,           KC_V,           KC_Z,           KC_TRANSPARENT, 
    KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT,                                                                                                 KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, 
    KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT,                 KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT
  ),
  [2] = LAYOUT_moonlander(
    KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT,                                 KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, 
    KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT,                                 KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, 
    KC_LEFT_SHIFT,  KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT,                                                                 KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, 
    KC_LEFT_CTRL,   KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT,                                 KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_RIGHT_SHIFT, 
    KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT,                                                                                                 KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, 
    KC_SPACE,       KC_TRANSPARENT, KC_TRANSPARENT,                 KC_TRANSPARENT, KC_TRANSPARENT, KC_ENTER
  ),
  [3] = LAYOUT_moonlander(
    KC_ESCAPE,      KC_F1,          KC_F2,          KC_F3,          KC_F4,          KC_F5,          KC_TRANSPARENT,                                 KC_TRANSPARENT, KC_F6,          KC_F7,          KC_F8,          KC_F9,          KC_F10,         KC_F11,         
    KC_TRANSPARENT, KC_EXLM,        KC_AT,          KC_LCBR,        KC_RCBR,        KC_PIPE,        KC_TRANSPARENT,                                 KC_HOME,        KC_END,         KC_7,           KC_8,           KC_9,           KC_ASTR,        KC_F12,         
    KC_TRANSPARENT, KC_HASH,        KC_DLR,         KC_LPRN,        KC_RPRN,        KC_GRAVE,       KC_TRANSPARENT,                                                                 KC_AMPR,        KC_PAGE_UP,     KC_4,           KC_5,           KC_6,           KC_KP_PLUS,     KC_TRANSPARENT, 
    KC_TRANSPARENT, KC_PERC,        KC_CIRC,        KC_LBRC,        KC_RBRC,        KC_TILD,                                        KC_PGDN,        KC_1,           KC_2,           KC_3,           KC_BSLS,        KC_TRANSPARENT, 
    KC_TRANSPARENT, KC_COMMA,       KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT,                                                                                                 KC_TRANSPARENT, KC_TRANSPARENT, KC_HOME,        KC_PGDN,        KC_PAGE_UP,     KC_END,         
    KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT,                 KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT
  ),
  [4] = LAYOUT_moonlander(
    TO(0),          TO(1),          TO(2),          TO(3),          KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT,                                 QK_BOOT,        KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, 
    KC_TRANSPARENT, TOGGLE_LAYER_COLOR,RGB_SLD,        RGB_MODE_FORWARD,RGB_TOG,        QK_AUDIO_ON,    KC_TRANSPARENT,                                 KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, 
    KC_TRANSPARENT, RGB_SPD,        RGB_SPI,        RGB_HUD,        RGB_HUI,        QK_AUDIO_OFF,   KC_TRANSPARENT,                                                                 KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, 
    KC_TRANSPARENT, RGB_VAD,        RGB_VAI,        KC_TRANSPARENT, KC_TRANSPARENT, MU_TOGG,                                        KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, 
    KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT,                                                                                                 KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT, 
    KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT,                 KC_TRANSPARENT, KC_TRANSPARENT, KC_TRANSPARENT
  ),
};





extern rgb_config_t rgb_matrix_config;

RGB hsv_to_rgb_with_value(HSV hsv) {
  RGB rgb = hsv_to_rgb( hsv );
  float f = (float)rgb_matrix_config.hsv.v / UINT8_MAX;
  return (RGB){ f * rgb.r, f * rgb.g, f * rgb.b };
}

void keyboard_post_init_user(void) {
  rgb_matrix_enable();
}

const uint8_t PROGMEM ledmap[][RGB_MATRIX_LED_COUNT][3] = {
    [0] = { {0,0,255}, {0,0,255}, {0,0,255}, {0,0,255}, {0,0,255}, {0,0,255}, {0,0,255}, {0,0,255}, {0,0,255}, {0,0,255}, {0,0,255}, {0,0,255}, {0,0,255}, {0,0,255}, {0,0,255}, {0,0,255}, {0,0,255}, {0,0,255}, {0,0,255}, {0,0,255}, {0,0,255}, {0,0,255}, {0,0,255}, {0,0,255}, {0,0,255}, {0,0,255}, {0,0,255}, {0,0,255}, {0,0,255}, {0,0,255}, {0,0,255}, {0,0,255}, {0,0,255}, {0,0,255}, {0,0,255}, {0,0,255}, {0,0,255}, {0,0,255}, {0,0,255}, {0,0,255}, {0,0,255}, {0,0,255}, {0,0,255}, {0,0,255}, {0,0,255}, {0,0,255}, {0,0,255}, {0,0,255}, {0,0,255}, {0,0,255}, {0,0,255}, {0,0,255}, {0,0,255}, {0,0,255}, {0,0,255}, {0,0,255}, {0,0,255}, {0,0,255}, {0,0,255}, {0,0,255}, {0,0,255}, {0,0,255}, {0,0,255}, {0,0,255}, {0,0,255}, {0,0,255}, {0,0,255}, {0,0,255}, {0,0,255}, {0,0,255}, {0,0,255}, {0,0,255} },

    [1] = { {12,255,252}, {12,255,252}, {12,255,252}, {12,255,252}, {12,255,252}, {12,255,252}, {12,255,252}, {12,255,252}, {12,255,252}, {12,255,252}, {12,255,252}, {12,255,252}, {12,255,252}, {12,255,252}, {12,255,252}, {12,255,252}, {12,255,252}, {12,255,252}, {12,255,252}, {12,255,252}, {12,255,252}, {12,255,252}, {12,255,252}, {12,255,252}, {12,255,252}, {12,255,252}, {12,255,252}, {12,255,252}, {12,255,252}, {12,255,252}, {12,255,252}, {12,255,252}, {12,255,252}, {12,255,252}, {12,255,252}, {12,255,252}, {12,255,252}, {12,255,252}, {12,255,252}, {12,255,252}, {12,255,252}, {12,255,252}, {12,255,252}, {12,255,252}, {12,255,252}, {12,255,252}, {12,255,252}, {12,255,252}, {12,255,252}, {12,255,252}, {12,255,252}, {12,255,252}, {12,255,252}, {12,255,252}, {12,255,252}, {12,255,252}, {12,255,252}, {12,255,252}, {12,255,252}, {12,255,252}, {12,255,252}, {12,255,252}, {12,255,252}, {12,255,252}, {12,255,252}, {12,255,252}, {12,255,252}, {12,255,252}, {12,255,252}, {12,255,252}, {12,255,252}, {12,255,252} },

    [2] = { {67,255,255}, {67,255,255}, {67,255,255}, {67,255,255}, {67,255,255}, {67,255,255}, {67,255,255}, {211,255,252}, {67,255,255}, {67,255,255}, {67,255,255}, {211,255,252}, {211,255,252}, {67,255,255}, {67,255,255}, {67,255,255}, {67,255,255}, {211,255,252}, {67,255,255}, {67,255,255}, {67,255,255}, {67,255,255}, {67,255,255}, {67,255,255}, {67,255,255}, {67,255,255}, {67,255,255}, {67,255,255}, {67,255,255}, {67,255,255}, {67,255,255}, {67,255,255}, {67,255,255}, {67,255,255}, {67,255,255}, {67,255,255}, {67,255,255}, {67,255,255}, {67,255,255}, {67,255,255}, {67,255,255}, {67,255,255}, {67,255,255}, {67,255,255}, {67,255,255}, {67,255,255}, {67,255,255}, {67,255,255}, {67,255,255}, {67,255,255}, {67,255,255}, {67,255,255}, {67,255,255}, {67,255,255}, {67,255,255}, {67,255,255}, {67,255,255}, {67,255,255}, {67,255,255}, {67,255,255}, {67,255,255}, {67,255,255}, {67,255,255}, {67,255,255}, {67,255,255}, {67,255,255}, {67,255,255}, {67,255,255}, {67,255,255}, {67,255,255}, {67,255,255}, {67,255,255} },

    [3] = { {0,0,0}, {0,0,0}, {0,0,0}, {0,0,0}, {0,0,0}, {189,255,255}, {0,0,0}, {0,0,0}, {0,0,0}, {0,0,0}, {189,255,255}, {0,0,0}, {0,0,0}, {0,0,0}, {0,0,0}, {189,255,255}, {0,0,0}, {0,0,0}, {0,0,0}, {0,0,0}, {189,255,255}, {0,0,0}, {0,0,0}, {0,0,0}, {0,0,0}, {189,255,255}, {0,0,0}, {0,0,0}, {0,0,0}, {0,0,0}, {0,0,0}, {0,0,0}, {0,0,0}, {0,0,0}, {0,0,0}, {0,0,0}, {189,255,255}, {189,255,255}, {0,0,0}, {0,0,0}, {196,255,255}, {189,255,255}, {0,255,252}, {0,255,252}, {0,255,252}, {196,255,255}, {189,255,255}, {67,255,255}, {67,255,255}, {67,255,255}, {196,255,255}, {189,255,255}, {67,255,255}, {67,255,255}, {67,255,255}, {196,255,255}, {189,255,255}, {67,255,255}, {67,255,255}, {67,255,255}, {0,0,0}, {189,255,255}, {45,255,252}, {45,255,252}, {45,255,252}, {0,0,0}, {45,255,252}, {0,0,0}, {0,0,0}, {0,0,0}, {0,0,0}, {0,0,0} },

    [4] = { {0,0,255}, {0,0,0}, {0,0,0}, {0,0,0}, {0,0,0}, {12,255,252}, {0,0,255}, {0,0,0}, {0,0,99}, {0,0,0}, {67,255,255}, {0,0,92}, {0,0,0}, {0,0,255}, {0,0,0}, {211,255,252}, {16,255,252}, {0,255,255}, {0,0,0}, {0,0,0}, {0,0,0}, {0,0,0}, {196,255,255}, {0,0,0}, {0,0,0}, {0,0,0}, {67,255,255}, {0,255,255}, {189,255,255}, {0,0,0}, {0,0,0}, {0,0,0}, {0,0,0}, {0,0,0}, {0,0,0}, {0,0,0}, {0,0,0}, {0,0,0}, {0,0,0}, {0,0,0}, {0,0,0}, {0,0,0}, {0,0,0}, {0,0,0}, {0,0,0}, {0,0,0}, {0,0,0}, {0,0,0}, {0,0,0}, {0,0,0}, {0,0,0}, {0,0,0}, {0,0,0}, {0,0,0}, {0,0,0}, {0,0,0}, {0,0,0}, {0,0,0}, {0,0,0}, {0,0,0}, {0,0,0}, {0,0,0}, {0,0,0}, {0,0,0}, {0,0,0}, {0,255,255}, {0,0,0}, {0,0,0}, {0,0,0}, {0,0,0}, {0,0,0}, {0,0,0} },

};

void set_layer_color(int layer) {
  for (int i = 0; i < RGB_MATRIX_LED_COUNT; i++) {
    HSV hsv = {
      .h = pgm_read_byte(&ledmap[layer][i][0]),
      .s = pgm_read_byte(&ledmap[layer][i][1]),
      .v = pgm_read_byte(&ledmap[layer][i][2]),
    };
    if (!hsv.h && !hsv.s && !hsv.v) {
        rgb_matrix_set_color( i, 0, 0, 0 );
    } else {
        RGB rgb = hsv_to_rgb_with_value(hsv);
        rgb_matrix_set_color(i, rgb.r, rgb.g, rgb.b);
    }
  }
}

bool rgb_matrix_indicators_user(void) {
  if (rawhid_state.rgb_control) {
      return false;
  }
  if (!keyboard_config.disable_layer_led) { 
    switch (biton32(layer_state)) {
      case 0:
        set_layer_color(0);
        break;
      case 1:
        set_layer_color(1);
        break;
      case 2:
        set_layer_color(2);
        break;
      case 3:
        set_layer_color(3);
        break;
      case 4:
        set_layer_color(4);
        break;
     default:
        if (rgb_matrix_get_flags() == LED_FLAG_NONE) {
          rgb_matrix_set_color_all(0, 0, 0);
        }
    }
  } else {
    if (rgb_matrix_get_flags() == LED_FLAG_NONE) {
      rgb_matrix_set_color_all(0, 0, 0);
    }
  }

  return true;
}


typedef struct {
    bool is_press_action;
    uint8_t step;
} tap;

enum {
    SINGLE_TAP = 1,      
    SINGLE_HOLD,         
    DOUBLE_TAP,          
    DOUBLE_HOLD,         
    DOUBLE_SINGLE_TAP,   
    MORE_TAPS            
};

static tap dance_state[1];

uint8_t dance_step(tap_dance_state_t *state);

uint8_t dance_step(tap_dance_state_t *state) {
    if (state->count == 1) {
        if (state->interrupted || !state->pressed) return SINGLE_TAP;
        else return SINGLE_HOLD;
    } else if (state->count == 2) {
        if (state->interrupted) return DOUBLE_SINGLE_TAP;
        else if (state->pressed) return DOUBLE_HOLD;
        else return DOUBLE_TAP;
    }
    return MORE_TAPS;
}


void on_dance_0(tap_dance_state_t *state, void *user_data);
void dance_0_finished(tap_dance_state_t *state, void *user_data);
void dance_0_reset(tap_dance_state_t *state, void *user_data);

void on_dance_0(tap_dance_state_t *state, void *user_data) {
    if(state->count == 3) {
        tap_code16(KC_NUM);
        tap_code16(KC_NUM);
        tap_code16(KC_NUM);
    }
    if(state->count > 3) {
        tap_code16(KC_NUM);
    }
}

void dance_0_finished(tap_dance_state_t *state, void *user_data) {
    dance_state[0].step = dance_step(state);
    switch (dance_state[0].step) {
        case SINGLE_TAP: register_code16(KC_NUM); break;
        case DOUBLE_TAP: register_code16(KC_SCRL); break;
        case DOUBLE_SINGLE_TAP: tap_code16(KC_NUM); register_code16(KC_NUM);
    }
}

void dance_0_reset(tap_dance_state_t *state, void *user_data) {
    wait_ms(10);
    switch (dance_state[0].step) {
        case SINGLE_TAP: unregister_code16(KC_NUM); break;
        case DOUBLE_TAP: unregister_code16(KC_SCRL); break;
        case DOUBLE_SINGLE_TAP: unregister_code16(KC_NUM); break;
    }
    dance_state[0].step = 0;
}

tap_dance_action_t tap_dance_actions[] = {
        [DANCE_0] = ACTION_TAP_DANCE_FN_ADVANCED(on_dance_0, dance_0_finished, dance_0_reset),
};

bool process_record_user(uint16_t keycode, keyrecord_t *record) {
  switch (keycode) {

    case RGB_SLD:
        if (rawhid_state.rgb_control) {
            return false;
        }
        if (record->event.pressed) {
            rgblight_mode(1);
        }
        return false;
  }
  return true;
}

