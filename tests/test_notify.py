from shop import notify


def test_sms_truncates():
    notify.SENT.clear()
    notify.notify_sms("x" * 200)
    assert len(notify.SENT[0][1]) == 160
