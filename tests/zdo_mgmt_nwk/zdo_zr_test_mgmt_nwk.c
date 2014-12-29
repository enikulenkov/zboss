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
PURPOSE: Test for ZC application written using ZDO.
*/


#include "zb_common.h"
#include "zb_scheduler.h"
#include "zb_bufpool.h"
#include "zb_nwk.h"
#include "zb_aps.h"
#include "zb_zdo.h"


/*! \addtogroup ZB_TESTS */
/*! @{ */

void data_indication(zb_uint8_t param) ZB_CALLBACK;
void new_active_channel_cb(zb_uint8_t param) ZB_CALLBACK;
void new_channel_mask_cb(zb_uint8_t param) ZB_CALLBACK;
void channel_scan_cb(zb_uint8_t param) ZB_CALLBACK;
void channel_scan_cb_error_1(zb_uint8_t param) ZB_CALLBACK;
void channel_scan_cb_error_2(zb_uint8_t param) ZB_CALLBACK;

static zb_int_t g_error_counter = 0;

#define TEST_CHANNEL_1 (1 << 11)
#define TEST_CHANNEL_2 (1 << 12)
#define TEST_CHANNEL_3 (1 << 13)
#define TEST_SCAN_DURATION 2
#define TEST_SCAN_COUNT    3
#define TEST_MANAGER_ADDR 0xBEAF
#define TEST_SCAN_DURATION_ERROR 10 /* incorrect value */
#define TEST_SCAN_COUNT_ERROR 15 /* incorrect value */

/*
  ZR joins to ZC, then sends APS packet.
 */


MAIN()
{
  ARGV_UNUSED;

#ifndef KEIL
  if ( argc < 3 )
  {
    printf("%s <read pipe path> <write pipe path>\n", argv[0]);
    return 0;
  }
#endif

  /* Init device, load IB values from nvram or set it to default */
#ifndef ZB8051
  ZB_INIT("zdo_zr", argv[1], argv[2]);
#else
  ZB_INIT("zdo_zr", "2", "2");
#endif
#ifdef ZB_SECURITY
  ZG->nwk.nib.security_level = 0;
#endif

  zb_set_default_ffd_descriptor_values(ZB_ROUTER);

  /* FIXME: temporary, until neighbor table is not in nvram */
  /* add extended address of potential parent to emulate that we've already
   * been connected to it */
  {
    zb_ieee_addr_t ieee_address;
    zb_address_ieee_ref_t ref;

    ZB_64BIT_ADDR_ZERO(ieee_address);
    ieee_address[7] = 8;

    zb_address_update(ieee_address, 0, ZB_FALSE, &ref);
  }

  if (zdo_dev_start() != RET_OK)
  {
    TRACE_MSG(TRACE_ERROR, "zdo_dev_start failed", (FMT__0));
  }
  else
  {
    zdo_main_loop();
  }

  TRACE_DEINIT();

  MAIN_RETURN(0);
}

void func1()
{
  zb_buf_t *asdu;
  zb_zdo_mgmt_nwk_update_req_t *req;

  asdu = zb_get_out_buf();
  if (!asdu)
  {
    TRACE_MSG(TRACE_ERROR, "out buf alloc failed!", (FMT__0));
  }
  else
  {
    req = ZB_GET_BUF_PARAM(asdu, zb_zdo_mgmt_nwk_update_req_t);

    req->hdr.scan_channels = TEST_CHANNEL_1;
    req->hdr.scan_duration = ZB_ZDO_NEW_ACTIVE_CHANNEL;
    req->update_id = ZB_NIB_UPDATE_ID();
    req->dst_addr = 0; //send to coordinator

    zb_zdo_mgmt_nwk_update_req(ZB_REF_FROM_BUF(asdu), new_active_channel_cb);
  }
}

void new_active_channel_cb(zb_uint8_t param) ZB_CALLBACK
{
  zb_buf_t *buf = ZB_BUF_FROM_REF(param);
  zb_zdo_mgmt_nwk_update_req_t *req;

  if (buf->u.hdr.status == RET_OK)
  {
    TRACE_MSG(TRACE_APS1, "zb_zdo_mgmt_nwk_update_req: new active channel Ok", (FMT__0));
  }
  else
  {
    TRACE_MSG(TRACE_APS1, "Error in zb_zdo_mgmt_nwk_update_req: new active channel", (FMT__0));
    g_error_counter++;
  }

  req = ZB_GET_BUF_PARAM(buf, zb_zdo_mgmt_nwk_update_req_t);

  req->hdr.scan_channels = TEST_CHANNEL_2;
  req->hdr.scan_duration = ZB_ZDO_NEW_CHANNEL_MASK;
  req->manager_addr = TEST_MANAGER_ADDR;
  req->update_id = ZB_NIB_UPDATE_ID();
  req->dst_addr = 0; //send to coordinator

  zb_zdo_mgmt_nwk_update_req(ZB_REF_FROM_BUF(buf), new_channel_mask_cb);
}

void new_channel_mask_cb(zb_uint8_t param) ZB_CALLBACK
{
  zb_buf_t *buf = ZB_BUF_FROM_REF(param);
  zb_zdo_mgmt_nwk_update_req_t *req;

  if (buf->u.hdr.status == RET_OK)
  {
    TRACE_MSG(TRACE_APS1, "zb_zdo_mgmt_nwk_update_req: new channel mask Ok", (FMT__0));
  }
  else
  {
    TRACE_MSG(TRACE_APS1, "Error in zb_zdo_mgmt_nwk_update_req: new channel mask", (FMT__0));
    g_error_counter++;
  }

  req = ZB_GET_BUF_PARAM(buf, zb_zdo_mgmt_nwk_update_req_t);
  req->hdr.scan_channels = TEST_CHANNEL_1 | TEST_CHANNEL_2 | TEST_CHANNEL_3;
  req->hdr.scan_duration = TEST_SCAN_DURATION;
  req->scan_count = TEST_SCAN_COUNT;
  req->update_id = ZB_NIB_UPDATE_ID();
  req->dst_addr = 0; //send to coordinator

  zb_zdo_mgmt_nwk_update_req(ZB_REF_FROM_BUF(buf), channel_scan_cb);
}

static zb_uint_t g_test_scan_count = 0;
void channel_scan_cb(zb_uint8_t param) ZB_CALLBACK
{
  zb_buf_t *buf = ZB_BUF_FROM_REF(param);
  zb_uint_t start_test = 0;
  zb_zdo_mgmt_nwk_update_req_t *req;

  g_test_scan_count++;
  if (buf->u.hdr.status == RET_OK)
  {
    TRACE_MSG(TRACE_APS1, "zb_zdo_mgmt_nwk_update_req: channel scan %d Ok, total scan count %d",
              (FMT__D_D, g_test_scan_count, TEST_SCAN_COUNT));
  }
  else
  {
    TRACE_MSG(TRACE_APS1, "Error in zb_zdo_mgmt_nwk_update_req: channel scan %d Ok, total scan count %d",
              (FMT__D_D, g_test_scan_count, TEST_SCAN_COUNT));
    g_error_counter++;
    start_test = 1;
  }

  if (g_test_scan_count == TEST_SCAN_COUNT)
  {
    TRACE_MSG(TRACE_APS1, "zb_zdo_mgmt_nwk_update_req: channel scan is finished OK", (FMT__0));
    start_test = 1;
  }

  if (start_test)
  {
    /* start next test */
    req = ZB_GET_BUF_PARAM(buf, zb_zdo_mgmt_nwk_update_req_t);
    req->hdr.scan_channels = TEST_CHANNEL_1 | TEST_CHANNEL_2 | TEST_CHANNEL_3;
    req->hdr.scan_duration = TEST_SCAN_DURATION_ERROR;
    req->scan_count = TEST_SCAN_COUNT;
    req->update_id = ZB_NIB_UPDATE_ID();
    req->dst_addr = 0; //send to coordinator

    zb_zdo_mgmt_nwk_update_req(ZB_REF_FROM_BUF(buf), channel_scan_cb_error_1);
  }
  else
  {
    zb_free_buf(buf);
  }
}


void channel_scan_cb_error_1(zb_uint8_t param) ZB_CALLBACK
{
  zb_buf_t *buf = ZB_BUF_FROM_REF(param);
  zb_zdo_mgmt_nwk_update_req_t *req;
  zb_zdo_mgmt_nwk_update_notify_hdr_t *notify_resp = (zb_zdo_mgmt_nwk_update_notify_hdr_t *)ZB_BUF_BEGIN(buf);

  if (notify_resp->status == RET_OK)
  {
    TRACE_MSG(TRACE_APS1, "zb_zdo_mgmt_nwk_update_req: error should come, received Ok - Error",
              (FMT__0));
    g_error_counter++;
  }
  else
  {
    TRACE_MSG(TRACE_APS1, "zb_zdo_mgmt_nwk_update_req: error code in response - Ok",
              (FMT__0));

  }

  /* start next test */
  req = ZB_GET_BUF_PARAM(buf, zb_zdo_mgmt_nwk_update_req_t);
  req->hdr.scan_channels = TEST_CHANNEL_1 | TEST_CHANNEL_2 | TEST_CHANNEL_3;
  req->hdr.scan_duration = TEST_SCAN_DURATION;
  req->scan_count = TEST_SCAN_COUNT_ERROR;
  req->update_id = ZB_NIB_UPDATE_ID();
  req->dst_addr = 0; //send to coordinator

  zb_zdo_mgmt_nwk_update_req(ZB_REF_FROM_BUF(buf), channel_scan_cb_error_2);

}

void channel_scan_cb_error_2(zb_uint8_t param) ZB_CALLBACK
{
  zb_buf_t *buf = ZB_BUF_FROM_REF(param);
  zb_zdo_mgmt_nwk_update_notify_hdr_t *notify_resp = (zb_zdo_mgmt_nwk_update_notify_hdr_t *)ZB_BUF_BEGIN(buf);

  if (notify_resp->status == RET_OK)
  {
    TRACE_MSG(TRACE_APS1, "zb_zdo_mgmt_nwk_update_req: error (2) should come, received Ok - Error",
              (FMT__0));
    g_error_counter++;
  }
  else
  {
    TRACE_MSG(TRACE_APS1, "zb_zdo_mgmt_nwk_update_req: error (2) code in response - Ok",
              (FMT__0));

  }
  zb_free_buf(buf);

  if (g_error_counter)
  {
    TRACE_MSG(TRACE_APS1, "Errors found in test %d", (FMT__D, g_error_counter));
  }
  else
  {
    TRACE_MSG(TRACE_APS1, "Test finished OK", (FMT__0));
  }
}

void zb_zdo_startup_complete(zb_uint8_t param) ZB_CALLBACK
{
  zb_buf_t *buf = ZB_BUF_FROM_REF(param);
  if (buf->u.hdr.status == 0)
  {
    TRACE_MSG(TRACE_APS1, "Device STARTED OK", (FMT__0));
    zb_af_set_data_indication(data_indication);
    //send_data((zb_buf_t *)ZB_BUF_FROM_REF(param));
    func1();
  }
  else
  {
    TRACE_MSG(TRACE_ERROR, "Device started FAILED status %d", (FMT__D, (int)buf->u.hdr.status));
    zb_free_buf(buf);
  }
}


void data_indication(zb_uint8_t param)
{
  zb_ushort_t i;
  zb_uint8_t *ptr;
  zb_buf_t *asdu = (zb_buf_t *)ZB_BUF_FROM_REF(param);

  /* Remove APS header from the packet */
  ZB_APS_HDR_CUT_P(asdu, ptr);

  TRACE_MSG(TRACE_APS3, "data_indication: packet %p len %d handle 0x%x", (FMT__P_D_D,
                         asdu, (int)ZB_BUF_LEN(asdu), asdu->u.hdr.status));

  for (i = 0 ; i < ZB_BUF_LEN(asdu) ; ++i)
  {
    TRACE_MSG(TRACE_APS3, "%x %c", (FMT__D_C, (int)ptr[i], ptr[i]));
  }

  //send_data(asdu);
}



/*! @} */
