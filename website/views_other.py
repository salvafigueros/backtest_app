from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify, Response, send_file
from .journal import Journal
from .user import User
from .journalForm import JournalForm, ViewJournalForm
from .backtestingManualForm import BacktestingManualForm, BacktestingManualFormProfit, BacktestingManualFormLoss
from .backtestingManual import BacktestingManual
from .backtestingManualOperation import BacktestingManualOperation
from functools import wraps

#Chart
import io
import base64
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.figure import Figure


views_other = Blueprint('views_other', __name__)


#Check if user is logged in
def is_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'log_in' in session:
            return f(*args, **kwargs)
        else:
            flash('Acceso no autorizado. Por favor, inicia sesión', category='error')
            return redirect(url_for('auth.login'))
    return wrap


@views_other.route('/other/write-journal', methods=['GET', 'POST'])
@is_logged_in
def write_journal():
    form = JournalForm()
     
    if form.validate_on_submit():
        user_id = form.user_id.data 
        date = form.date.data
        text = form.journal_text.data

        journal = Journal.create_journal(user_id, date, text)

        if journal:
            return redirect(url_for('views_other.journal', id = journal.id))



    return render_template("write_journal.html", form=form)


@views_other.route('/other/journal', methods=['GET'])
@is_logged_in
def journal():
    journal_id = request.args.get('id')

    if journal_id:
        journal = Journal.get_journal_by_id(journal_id)

        if journal and journal.user_id == session["user_id"]:
            return render_template("journal.html", journal=journal, user=User.get_user_by_id(journal.user_id))

    return redirect(url_for('views.home'))


@views_other.route('/other/journal-user', methods=['GET'])
@is_logged_in
def list_journal():
    user_id = request.args.get('id')

    if user_id:
        user_id = int(user_id)

    if user_id and user_id == session["user_id"]:
        list_journal = Journal.get_list_journal_by_user_id(user_id)

        return render_template("search_journal_user.html", list_journal=list_journal, user=User.get_user_by_id(user_id))

    return redirect(url_for('views.home'))


@views_other.route('/other/backtesting-manual-pre', methods=['GET', 'POST'])
def backtesting_manual_form():
    form = BacktestingManualForm()

    if form.validate_on_submit():
        starting_cash = form.starting_cash.data
        currency = form.currency.data

        backtesting_manual = BacktestingManual.create_backtesting_manual(session["user_id"], starting_cash, currency)

        if backtesting_manual:
            return redirect(url_for('views_other.backtesting_manual', backtesting_manual_id=backtesting_manual.id))
    
    return render_template("backtesting_manual_form.html", form=form)



@views_other.route('/other/backtesting-manual', methods=['GET', 'POST'])
def backtesting_manual():
    form_profit = BacktestingManualFormProfit()
    form_loss = BacktestingManualFormLoss()

    backtesting_manual_id = request.args.get('backtesting_manual_id') 
    backtesting_manual = BacktestingManual.get_backtesting_manual_by_id(backtesting_manual_id)

    if backtesting_manual and backtesting_manual.user_id == session["user_id"]:
        return render_template("backtesting_manual.html", backtesting_manual=backtesting_manual, form_profit=form_profit, form_loss=form_loss)
    
    return redirect(url_for('views.home'))


@views_other.route('/other/backtesting-manual-profit', methods=['POST'])
def backtesting_manual_process_profit():
    form = BacktestingManualFormProfit()

    if form.validate_on_submit():
        profit = form.profit.data
        backtesting_manual_id = form.backtesting_id.data
        date = form.date.data

        backtesting_manual_operation = BacktestingManualOperation.create_backtesting_manual_operation(backtesting_manual_id, profit, date)
        backtesting_manual = BacktestingManual.get_backtesting_manual_by_id(backtesting_manual_id)

        return jsonify(data={'message': 'Profit {}'.format(profit),
                        'capital': backtesting_manual.capital_now,
                        'pnl': backtesting_manual.pnl_return,
                        'total_trades': backtesting_manual.total_trades,
                        'total_wins': backtesting_manual.total_wins,
                        'total_losses': backtesting_manual.total_losses})

    return jsonify(data=form.errors)


@views_other.route('/other/backtesting-manual-loss', methods=['POST'])
def backtesting_manual_process_loss():
    form = BacktestingManualFormLoss()

    if form.validate_on_submit():
        loss = form.loss.data
        backtesting_manual_id = form.backtesting_id.data
        date = form.date.data

        backtesting_manual_operation = BacktestingManualOperation.create_backtesting_manual_operation(backtesting_manual_id, -loss, date)
        backtesting_manual = BacktestingManual.get_backtesting_manual_by_id(backtesting_manual_id)

        return jsonify(data={'message': 'Loss {}'.format(loss),
                             'capital': backtesting_manual.capital_now,
                             'pnl': backtesting_manual.pnl_return,
                             'total_trades': backtesting_manual.total_trades,
                             'total_wins': backtesting_manual.total_wins,
                             'total_losses': backtesting_manual.total_losses})

    return jsonify(data=form.errors)


@views_other.route('/other/backtesting-manual-chart', methods=['GET', 'POST'])
def backtesting_manual_chart():
    backtesting_manual_id = request.args.get('backtesting_manual_id') 
    backtesting_manual = BacktestingManual.get_backtesting_manual_by_id(backtesting_manual_id)

    if backtesting_manual:
        df = backtesting_manual.equity_curve_df

        fig, ax = plt.subplots(figsize=(6,6))
        ax = sns.set(style="darkgrid")
        sns.lineplot(data=df, x=df.index, y="Equity Curve")
        canvas = FigureCanvas(fig)
        img = io.BytesIO()
        fig.savefig(img)
        img.seek(0)

    return send_file(img, mimetype='img/png')


@views_other.route('/other/backtesting-manual/save', methods=['POST'])
def backtesting_manual_save():
    backtesting = request.get_json()
    backtesting_manual = BacktestingManual.get_backtesting_manual_by_id(backtesting['backtesting_manual_id'])
    backtesting_manual.saved = True
    backtesting_manual.name = backtesting['backtesting_manual_name']
    backtesting_manual.user_id = session["user_id"]
    backtesting_manual = BacktestingManual.save_backtesting_manual(backtesting_manual)
    
    return jsonify({})


@views_other.route('/other/backtesting-manual-user', methods=['GET'])
@is_logged_in
def list_backtesting_manual():
    user_id = request.args.get('id')

    if user_id:
        user_id = int(user_id)


    if (user_id) and (user_id == session["user_id"]):
        list_backtesting_manual = BacktestingManual.get_list_backtesting_manual_by_user_id(user_id)
        list_backtesting_manual = [backtesting for backtesting in list_backtesting_manual if backtesting.saved == True]

        return render_template("search_backtesting_manual_user.html", list_backtesting_manual=list_backtesting_manual, user=User.get_user_by_id(user_id))

    return redirect(url_for('views.home')) 



