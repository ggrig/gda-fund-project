/*
 * lws-bybit
 *
 * Written in 2010-2021 by Andy Green <andy@warmcat.com>
 *                         Kutoga <kutoga@user.github.invalid>
 *
 * This file is made available under the Creative Commons CC0 1.0
 * Universal Public Domain Dedication.
 *
 * This demonstrates a Secure Streams implementation of a client that connects
 * to binance ws server efficiently.
 *
 * Build lws with -DLWS_WITH_SECURE_STREAMS=1 -DLWS_WITHOUT_EXTENSIONS=0
 *
 * "policy.json" contains all the information about endpoints, protocols and
 * connection validation, tagged by streamtype name.
 *
 * The example tries to load it from the cwd, it lives
 * in ./minimal-examples/secure-streams/minimal-secure-streams-binance dir, so
 * either run it from there, or copy the policy.json to your cwd.  It's also
 * possible to put the policy json in the code as a string and pass that at
 * context creation time.
 */
#define _GNU_SOURCE

#include <libwebsockets.h>
#include <string.h>
#include <signal.h>
#include <ctype.h>

#include <stdio.h>
#include <string.h>
#include <fcntl.h>
#include <sys/stat.h>
#include <sys/types.h>
#include <unistd.h>

extern int test_result;
extern char topic[64];
extern char fifo[64];
int fifo_descriptor = -1;
int read_counter = 0;

typedef struct range {
	uint64_t		sum;
	uint64_t		lowest;
	uint64_t		highest;

	unsigned int		samples;
} range_t;

LWS_SS_USER_TYPEDEF
	lws_sorted_usec_list_t	sul_hz;	     /* 1hz summary dump */

	range_t			e_lat_range;
	range_t			price_range;

	char			msg[64];
	const char		*payload;
	size_t			size;
	size_t			pos;

	int			count;
} bybit_t;

static uint64_t
get_us_timeofday(void)
{
	struct timeval tv;

	gettimeofday(&tv, NULL);

	return (uint64_t)((lws_usec_t)tv.tv_sec * LWS_US_PER_SEC) +
			  (uint64_t)tv.tv_usec;
}

static void
sul_hz_cb(lws_sorted_usec_list_t *sul)
{
	bybit_t *bin = lws_container_of(sul, bybit_t, sul_hz);
	bybit_t *g = bin;

	// /* provide a hint about the payload size */
	g->pos = 0;
	g->payload = g->msg;
	g->size = (size_t)lws_snprintf(g->msg, sizeof(g->msg),
					"{\"op\": \"subscribe\", \"args\": [\"%s\"]}",topic);

	if (lws_ss_request_tx_len(lws_ss_from_user(g), (unsigned long)g->size))
		lwsl_notice("%s: req failed\n", __func__);

	/*
	 * We are called once a second to dump statistics on the connection
	 */

	lws_sul_schedule(lws_ss_get_context(bin->ss), 0, &bin->sul_hz,
			 sul_hz_cb, LWS_US_PER_SEC);
}

static lws_ss_state_return_t
bybit_transfer_callback(void *userobj, lws_ss_tx_ordinal_t ord, uint8_t *buf, size_t *len,
	     int *flags)
{
	bybit_t *bin = (bybit_t *)userobj;
	lws_ss_state_return_t r = LWSSSSRET_OK;
	bybit_t *g = bin;

	lwsl_debug("bybit_transfer_callback");

	if (g->size == g->pos)
		return LWSSSSRET_TX_DONT_SEND;

	if (*len > g->size - g->pos)
		*len = g->size - g->pos;

	if (!g->pos)
		*flags |= LWSSS_FLAG_SOM;

	memcpy(buf, g->payload + g->pos, *len);
	g->pos += *len;

	if (g->pos != g->size)
		/* more to do */
		r = lws_ss_request_tx(lws_ss_from_user(g));
	else
		*flags |= LWSSS_FLAG_EOM;

	lwsl_ss_user(lws_ss_from_user(g), "TX %zu, flags 0x%x, r %d", *len,
					  (unsigned int)*flags, (int)r);

	return r;
}

static lws_ss_state_return_t
bybit_receive_callback(void *userobj, const uint8_t *in, size_t len, int flags)
{
	bybit_t *bin = (bybit_t *)userobj;
	uint64_t latency_us, now_us;
	char numbuf[16];
	uint64_t price;
	const char *p;
	size_t alen;

	// now_us = (uint64_t)get_us_timeofday();

	p = lws_json_simple_find((const char *)in, len, "\"topic\"",
				 &alen);
	if (!p)
		return LWSSSSRET_OK;

	if (lws_json_simple_find((const char *)in, len, "\"snapshot\"", &alen))
		lwsl_user("Snapshot at index %d", read_counter);

	// lwsl_debug("%s", in);
	if (fifo_descriptor >= 0) // the fifo is valid
	{
		// int cap = fcntl(fifo_descriptor, F_GETPIPE_SZ);
		// int line_len = strlen(in);

		// if (line_len >= 4096)
		// {
		// 	lwsl_user("Long line: %d \n", line_len);
		// 	return LWSSSSRET_OK;
		// }

		// if (line_len + 2 < cap)
		// {
		// 	write(fifo_descriptor, in, strlen(in));
		// 	write(fifo_descriptor, "\n", 1);
		// }

		write(fifo_descriptor, in, strlen(in));
		write(fifo_descriptor, "\n", 1);
		read_counter += 1;

	}

	return LWSSSSRET_OK;
}

static lws_ss_state_return_t
bybit_state(void *userobj, void *h_src, lws_ss_constate_t state,
	      lws_ss_tx_ordinal_t ack)
{
	bybit_t *bin = (bybit_t *)userobj;

	lwsl_ss_info(bin->ss, "%s (%d), ord 0x%x",
		     lws_ss_state_name((int)state), state, (unsigned int)ack);

	switch (state) {

	case LWSSSCS_CONNECTED:
		lws_sul_schedule(lws_ss_get_context(bin->ss), 0, &bin->sul_hz,
				 sul_hz_cb, LWS_US_PER_SEC);
		mkfifo(fifo, 0666);
		fifo_descriptor = open(fifo, O_WRONLY);
		if (fifo_descriptor >= 0) // the fifo is valid
		{
			lwsl_debug("Pipe %s created",fifo);
		}
		return LWSSSSRET_OK;

	case LWSSSCS_DISCONNECTED:
		lws_sul_cancel(&bin->sul_hz);
		if (fifo_descriptor >= 0) // the fifo is valid
		{
			close(fifo_descriptor);
			fifo_descriptor = -1;
			lwsl_debug("Pipe %s closed",fifo);
			lwsl_user("Messages read %d", read_counter);
			read_counter = 0;
		}
		break;

	default:
		break;
	}

	return LWSSSSRET_OK;
}

LWS_SS_INFO("bybit", bybit_t)
	.rx           = bybit_receive_callback,
	.tx           = bybit_transfer_callback,
	.state        = bybit_state,
};
