"""Legal & intellectual-property guidance."""

from __future__ import annotations

import streamlit as st

from lib import ui


def render() -> None:
    ui.section("Legal & intellectual property")
    st.caption(
        "Plain-language summaries to help writers understand their rights. This is "
        "general information, not legal advice."
    )

    tabs = st.tabs(
        ["Your rights", "Fan fiction", "Copyright basics", "Licensing", "Terms & takedowns"]
    )

    with tabs[0]:
        st.markdown(
            """
#### You keep your rights
- **You own your work.** Posting on Inkverse does **not** transfer copyright to us.
  You grant Inkverse only a limited, non-exclusive license to host and display
  your work on the platform.
- **You can remove your work** at any time. Removal revokes our display license
  going forward.
- **Adaptations** (such as short films) require permission from the original
  author unless the work is in the public domain or the author has granted a
  license that allows it.
- **Attribution matters.** Always credit collaborators and original authors when
  contributing to shared universes.
            """
        )

    with tabs[1]:
        st.markdown(
            """
#### Fan fiction — read this first
Fan fiction uses characters and settings owned by other creators. It generally
lives in a legal grey area:

- **Transformative, non-commercial** fan works are often tolerated and may be
  defensible as fair use, but this is **not guaranteed**.
- **Do not sell** fan fiction or merchandise based on someone else's IP without a
  license.
- **Respect creator wishes.** Some rights-holders explicitly forbid fan works;
  others publish fan-content policies. Check before posting.
- Inkverse labels fan fiction clearly and will honor valid rights-holder
  takedown requests.
            """
        )

    with tabs[2]:
        st.markdown(
            """
#### Copyright basics
- **Ideas aren't protected — expression is.** You can't copyright a plot concept
  ("a wizard school"), but you can protect the specific way you express it.
- **Copyright is automatic** the moment you fix your work in a tangible form. You
  do not need to register to own it (though registration helps enforcement in
  some jurisdictions).
- **Common tropes are free to use.** "Chosen one", "enemies to lovers", and
  "heist gone wrong" belong to everyone.
- **Substantial similarity** of distinctive, expressive elements is what creates
  infringement risk. That's exactly what our AI checker helps you spot.
            """
        )

    with tabs[3]:
        st.markdown(
            """
#### Licensing your work
When you publish, you can choose how others may use your work:

- **All rights reserved** — others may read on Inkverse but not reuse.
- **Creative Commons (e.g. CC BY-NC)** — others may share/adapt under conditions
  such as attribution and non-commercial use.
- **Open collaboration** — for shared universes, contributors agree to the
  universe's canon rules and licensing terms set by its creator.

As an open-source platform, the **Inkverse software** is provided under an open
license, but **your stories remain yours** under whichever license you choose.
            """
        )
        st.info(
            "Tip: pick a license that matches your goals. Want adaptations and "
            "remixes? A permissive CC license invites collaboration. Want tight "
            "control? Keep all rights reserved."
        )

    with tabs[4]:
        st.markdown(
            """
#### Terms of use & takedowns (summary)
- **Don't post infringing content.** Run the originality check before publishing.
- **No plagiarism, hate speech, or illegal content.**
- **Takedown / DMCA-style process:** rights-holders can request removal of
  infringing material; we review and act on valid requests, and notify the
  affected user.
- **Repeat infringers** may have their accounts suspended.
- **No legal advice:** the originality checker and these pages are informational
  tools. For real disputes, consult a qualified attorney.
            """
        )

    st.divider()
    st.markdown(
        '<p class="ink-tag">Inkverse is an open-source project. The platform code is '
        "open; the stories belong to their authors.</p>",
        unsafe_allow_html=True,
    )
