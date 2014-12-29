/***************************************************************************
*                      ZBOSS ZigBee Pro 2007 stack                         *
*                                                                          *
*          Copyright (c) 2012 DSR Corporation Denver CO, USA.              *
*                       http://www.dsr-wireless.com                        *
*                                                                          *
*                            All rights reserved.                          *
*          Copyright (c) 2011 ClarIDy Solutions, Inc., Taipei, Taiwan.     *
*                       http://www.claridy.com/                            *
*                                                                          *
*          Copyright (c) 2011 Uniband Electronic Corporation (UBEC),       *
*                             Hsinchu, Taiwan.                             *
*                       http://www.ubec.com.tw/                            *
*                                                                          *
*          Copyright (c) 2011 DSR Corporation Denver CO, USA.              *
*                       http://www.dsr-wireless.com                        *
*                                                                          *
*                            All rights reserved.                          *
*                                                                          *
*                                                                          *
* ZigBee Pro 2007 stack, also known as ZBOSS (R) ZB stack is available     *
* under either the terms of the Commercial License or the GNU General      *
* Public License version 2.0.  As a recipient of ZigBee Pro 2007 stack, you*
* may choose which license to receive this code under (except as noted in  *
* per-module LICENSE files).                                               *
*                                                                          *
* ZBOSS is a registered trademark of DSR Corporation AKA Data Storage      *
* Research LLC.                                                            *
*                                                                          *
* GNU General Public License Usage                                         *
* This file may be used under the terms of the GNU General Public License  *
* version 2.0 as published by the Free Software Foundation and appearing   *
* in the file LICENSE.GPL included in the packaging of this file.  Please  *
* review the following information to ensure the GNU General Public        *
* License version 2.0 requirements will be met:                            *
* http://www.gnu.org/licenses/old-licenses/gpl-2.0.html.                   *
*                                                                          *
* Commercial Usage                                                         *
* Licensees holding valid ClarIDy/UBEC/DSR Commercial licenses may use     *
* this file in accordance with the ClarIDy/UBEC/DSR Commercial License     *
* Agreement provided with the Software or, alternatively, in accordance    *
* with the terms contained in a written agreement between you and          *
* ClarIDy/UBEC/DSR.                                                        *
*                                                                          *
****************************************************************************
PURPOSE: Hardware abstraction layer: general purpose I\O header file
*/

#ifndef ZB_HAL_GPIO_H
#define ZB_HAL_GPIO_H 1

#include "zb_common.h"
#include "zb_hal_platform.h"    /* zb_hal_port_width_t is defined here */

typedef enum
{
  ZB_HAL_GPIO_MODE_IN = 0,
  ZB_HAL_GPIO_MODE_OUT_PUSH_PULL,
  ZB_HAL_GPIO_MODE_OUT_OPEN_DRAIN,
  ZB_HAL_GPIO_MODE_ALTERNATE,
  ZB_HAL_GPIO_MODE_ANALOG,
} zb_hal_gpio_mode_e;

typedef enum
{
  ZB_HAL_GPIO_PULL_NO_PULL = 0,
  ZB_HAL_GPIO_PULL_PULL_UP,
  ZB_HAL_GPIO_PULL_PULL_DOWN,
} zb_hal_gpio_pull_e;

typedef enum
{
  ZB_HAL_GPIO_PORT_A = 0,
  ZB_HAL_GPIO_PORT_B,
  ZB_HAL_GPIO_PORT_C,
  ZB_HAL_GPIO_PORT_D,
  ZB_HAL_GPIO_PORT_E,
  ZB_HAL_GPIO_PORT_F,
  ZB_HAL_GPIO_PORT_G,
  ZB_HAL_GPIO_PORT_H
} zb_hal_gpio_port_e;

/* Definitions for MCUs that use numbered ports */
#define ZB_HAL_GPIO_PORT_0 ZB_HAL_GPIO_PORT_A
#define ZB_HAL_GPIO_PORT_1 ZB_HAL_GPIO_PORT_B
#define ZB_HAL_GPIO_PORT_2 ZB_HAL_GPIO_PORT_C
#define ZB_HAL_GPIO_PORT_3 ZB_HAL_GPIO_PORT_D
#define ZB_HAL_GPIO_PORT_4 ZB_HAL_GPIO_PORT_E
#define ZB_HAL_GPIO_PORT_5 ZB_HAL_GPIO_PORT_F
#define ZB_HAL_GPIO_PORT_6 ZB_HAL_GPIO_PORT_G
#define ZB_HAL_GPIO_PORT_7 ZB_HAL_GPIO_PORT_H

/* Add PIN16-PIN32 if they are needed. Actualy there are few number of MCUs with pin number
 * greater than 16
 */
#define ZB_HAL_GPIO_PIN_0  0x00000001
#define ZB_HAL_GPIO_PIN_1  0x00000002
#define ZB_HAL_GPIO_PIN_2  0x00000004
#define ZB_HAL_GPIO_PIN_3  0x00000008
#define ZB_HAL_GPIO_PIN_4  0x00000010
#define ZB_HAL_GPIO_PIN_5  0x00000020
#define ZB_HAL_GPIO_PIN_6  0x00000040
#define ZB_HAL_GPIO_PIN_7  0x00000080
#define ZB_HAL_GPIO_PIN_8  0x00000100
#define ZB_HAL_GPIO_PIN_9  0x00000200
#define ZB_HAL_GPIO_PIN_10 0x00000400
#define ZB_HAL_GPIO_PIN_11 0x00000800
#define ZB_HAL_GPIO_PIN_12 0x00001000
#define ZB_HAL_GPIO_PIN_13 0x00000400
#define ZB_HAL_GPIO_PIN_14 0x00000800
#define ZB_HAL_GPIO_PIN_15 0x00001000

typedef zb_uint8_t zb_hal_gpio_mode_t;
typedef zb_uint8_t zb_hal_gpio_pull_t;
typedef zb_uint8_t zb_hal_gpio_port_t;
typedef zb_uint32_t zb_hal_gpio_pin_t;


typedef struct zb_hal_gpio_init_s
{
  zb_hal_gpio_mode_t mode;
  zb_hal_gpio_pull_t pull;
  zb_hal_gpio_port_t port;
  zb_hal_gpio_pin_t  pin;              /* Bitmask */
} zb_hal_gpio_t;

/* Function prototypes */
zb_ret_t zb_hal_gpio_init(zb_hal_gpio_t *gpio_init);
zb_ret_t zb_hal_gpio_deinit(void);

zb_hal_port_width_t zb_hal_gpio_read_port(zb_hal_gpio_port_t port);

zb_ret_t zb_hal_gpio_write_port(zb_hal_gpio_port_t port,
                                zb_hal_port_width_t value);

zb_ret_t zb_hal_gpio_set_bit(zb_hal_gpio_port_t port,
                             zb_hal_gpio_pin_t pin);

zb_ret_t zb_hal_gpio_reset_bit(zb_hal_gpio_port_t port,
                               zb_hal_gpio_pin_t pin);

zb_ret_t zb_hal_gpio_write_bit(zb_hal_gpio_port_t port,
                               zb_hal_gpio_pin_t pin);

zb_uint8_t zb_hal_gpio_read_bit(zb_hal_gpio_port_t port,
                                zb_hal_gpio_pin_t pin);

#endif /* ZB_HAL_GPIO_H */
