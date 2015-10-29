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
PURPOSE: Header used by integration tests.
*/

#include "zb_common.h"
#include "zb_trace.h"

#ifndef ZB_SYSTEST_H
#define ZB_SYSTEST_H 1

enum zb_systest_err_lvl {
  ZB_SYSTEST_LVL_ERR,
  ZB_SYSTEST_LVL_WARN
};

void zb_systest_started();
void zb_systest_finished();
void zb_systest_error(enum zb_systest_err_lvl lvl, zb_char_t *fmt_str,
                      zb_char_t *file, zb_int_t line, zb_int_t args_size, ...);

#define ZB_SYSTEST_ERROR(fmt, args)                                         \
{                                                                           \
  TRACE_MSG(TRACE_ERROR, fmt, args);                                        \
  zb_systest_error(ZB_SYSTEST_LVL_ERR, fmt, _T0 args);                      \
}

#define ZB_SYSTEST_EXIT_ERR(fmt, args)                                      \
{                                                                           \
  ZB_SYSTEST_ERROR(fmt, args);                                              \
  zb_systest_finished();                                                    \
}

#define ZB_SYSTEST_WARN(fmt, args)                                          \
{                                                                           \
  TRACE_MSG(TRACE_INFO1, fmt, args);                                        \
  zb_systest_error(ZB_SYSTEST_LVL_WARN, fmt, _T0 args);                     \
}

#endif /* ZB_SYSTEST_H */
