from osd2f import config, utils
from osd2f.definitions import SubmissionList

from quart import Quart, render_template, request
from quart.json import jsonify


from .anonymizers import anonymize_submission_list
from .logger import logger

app = Quart(__name__)


@app.route("/")
async def home():
    return await render_template("home.html")


@app.route("/privacy")
async def privacy():
    return await render_template("privacy.html")


@app.route("/donate")
async def donate():
    return await render_template("donate.html")


@app.route("/upload", methods=["GET", "POST"])
async def upload():
    if request.method == "GET":
        # sid is an ID by which a referrer may identify
        # a user. This could for instance be the id that
        # a survey tool uses to match the survey response
        # to the submitted donation.
        sid = request.args.get("sid", "test")
        settings = utils.load_settings(force_disk=app.debug)
        return await render_template(
            "filesubmit.html", settings=settings.dict(), sid=sid
        )
    elif request.method == "POST":
        # TODO actually do something with the uploaded data
        data = await request.get_data()
        SubmissionList.parse_raw(data)
        logger.info("Received the donation!")
        return jsonify({"error": "", "data": ""}), 200


@app.route("/anonymize", methods=["POST"])
async def anonymize():
    data = await request.get_data()
    logger.debug(f"[anonymization] received: {data}")
    if len(data) == 0:
        return jsonify({"error": "no data received"}), 400

    settings = utils.load_settings(force_disk=app.debug)
    try:
        submission_list = SubmissionList.parse_raw(data)
    except ValueError as e:
        logger.debug(f"[anonymization] could not parse: {e}")
        return jsonify({"error": "incorrect submission format"}), 400

    submission_list = await anonymize_submission_list(
        submission_list=submission_list, settings=settings
    )

    return jsonify({"error": "", "data": submission_list.dict()["__root__"]}), 200


def start(mode: str = "Testing"):
    app.config.from_object(getattr(config, mode))

    # Check to make sure the application is never in production with a vacant key
    in_production_mode = mode == "Production"
    key_is_set = app.config["SECRET_KEY"] is not None
    if in_production_mode:
        logger.info("Starting app in production mode")
        assert key_is_set, ValueError(
            "To run OSD2F in production, the `OSD2F_SECRET` environment "
            "variable MUST be set."
        )

    app.run()
