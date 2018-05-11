import numpy
import pandas as pd
import math as m


# Moving Average
def MA(df, n):
    MA = pd.Series(pd.rolling_mean(df['close'], n), name='ma_' + str(n))
    df[MA.name] = MA
    return df


# Exponential Moving Average
def EMA(df, n):
    EMA = pd.Series(pd.ewma(df['close'], span=n, min_periods=n - 1), name='ema_' + str(n))
    df[EMA.name] = EMA

    return df


# Momentum
def MOM(df, n):
    M = pd.Series(df['close'].diff(n), name='momentum_' + str(n))
    df[M.name] = M
    return df


# Rate of Change
def ROC(df, n):
    M = df['close'].diff(n - 1)
    N = df['close'].shift(n - 1)
    ROC = pd.Series(M / N, name='roc_' + str(n))
    df[ROC.name] = ROC
    return df


# Average True Range
def ATR(df, n):
    i = 0
    TR_l = [0]
    while i < df.index[-1]:
        TR = max(df.get_value(i + 1, 'high'), df.get_value(i, 'close')) - min(df.get_value(i + 1, 'low'),
                                                                              df.get_value(i, 'close'))
        TR_l.append(TR)
        i = i + 1
    TR_s = pd.Series(TR_l)
    ATR = pd.Series(pd.ewma(TR_s, span=n, min_periods=n), name='atr_' + str(n))
    df[ATR.name] = ATR
    return df


# Bollinger Bands
def BBANDS(df, n):
    MA = pd.Series(pd.rolling_mean(df['close'], n))
    MSD = pd.Series(pd.rolling_std(df['close'], n))
    b1 = 4 * MSD / MA
    B1 = pd.Series(b1, name='bollingerb_' + str(n))
    df[B1.name] = B1
    b2 = (df['close'] - MA + 2 * MSD) / (4 * MSD)
    B2 = pd.Series(b2, name='bollinger%b_' + str(n))
    df[B2.name] = B2
    return df


# Pivot Points, Supports and Resistances
def PPSR(df):
    PP = pd.Series((df['high'] + df['low'] + df['close']) / 3)
    R1 = pd.Series(2 * PP - df['low'])
    S1 = pd.Series(2 * PP - df['high'])
    R2 = pd.Series(PP + df['high'] - df['low'])
    S2 = pd.Series(PP - df['high'] + df['low'])
    R3 = pd.Series(df['high'] + 2 * (PP - df['low']))
    S3 = pd.Series(df['low'] - 2 * (df['high'] - PP))
    psr = {'pp': PP, 'r1': R1, 's1': S1, 'r2': R2, 's2': S2, 'r3': R3, 's3': S3}
    PSR = pd.DataFrame(psr)
    df[PSR.name] = PSR
    return df


# Stochastic oscillator %K
def STOK(df):
    SOk = pd.Series((df['close'] - df['low']) / (df['high'] - df['low']), name='so%k')
    df[SOk.name] = SOk
    return df


# Stochastic oscillator %D
def STO(df, n):
    SOk = pd.Series((df['close'] - df['low']) / (df['high'] - df['low']), name='so%k')
    SOd = pd.Series(pd.ewma(SOk, span=n, min_periods=n - 1), name='SO%d_' + str(n))
    df[SOd.name] = SOd

    return df


# Trix
def TRIX(df, n):
    EX1 = pd.ewma(df['close'], span=n, min_periods=n - 1)
    EX2 = pd.ewma(EX1, span=n, min_periods=n - 1)
    EX3 = pd.ewma(EX2, span=n, min_periods=n - 1)
    i = 0
    ROC_l = [0]
    while i + 1 <= df.index[-1]:
        ROC = (EX3[i + 1] - EX3[i]) / EX3[i]
        ROC_l.append(ROC)
        i = i + 1
    Trix = pd.Series(ROC_l, name='trix_' + str(n))
    df[Trix.name] = Trix
    return df


# Average Directional Movement Index
def ADX(df, n, n_ADX):
    i = 0
    UpI = []
    DoI = []
    while i + 1 <= df.index[-1]:
        UpMove = df.get_value(i + 1, 'high') - df.get_value(i, 'high')
        DoMove = df.get_value(i, 'low') - df.get_value(i + 1, 'low')
        if UpMove > DoMove and UpMove > 0:
            UpD = UpMove
        else:
            UpD = 0
        UpI.append(UpD)
        if DoMove > UpMove and DoMove > 0:
            DoD = DoMove
        else:
            DoD = 0
        DoI.append(DoD)
        i = i + 1
    i = 0
    TR_l = [0]
    while i < df.index[-1]:
        TR = max(df.get_value(i + 1, 'high'), df.get_value(i, 'close')) - min(df.get_value(i + 1, 'low'),
                                                                              df.get_value(i, 'close'))
        TR_l.append(TR)
        i = i + 1
    TR_s = pd.Series(TR_l)
    ATR = pd.Series(pd.ewma(TR_s, span=n, min_periods=n))
    UpI = pd.Series(UpI)
    DoI = pd.Series(DoI)
    PosDI = pd.Series(pd.ewma(UpI, span=n, min_periods=n - 1) / ATR)
    NegDI = pd.Series(pd.ewma(DoI, span=n, min_periods=n - 1) / ATR)
    ADX = pd.Series(pd.ewma(abs(PosDI - NegDI) / (PosDI + NegDI), span=n_ADX, min_periods=n_ADX - 1),
                    name='adx_' + str(n) + '_' + str(n_ADX))
    df[ADX.name] = ADX
    return df


# MACD, MACD Signal and MACD difference
def MACD(df, n_fast, n_slow):
    EMAfast = pd.Series(pd.ewma(df['close'], span=n_fast, min_periods=n_slow - 1))
    EMAslow = pd.Series(pd.ewma(df['close'], span=n_slow, min_periods=n_slow - 1))
    MACD = pd.Series(EMAfast - EMAslow, name='macd_' + str(n_fast) + '_' + str(n_slow))
    MACDsign = pd.Series(pd.ewma(MACD, span=9, min_periods=8), name='macdsign_' + str(n_fast) + '_' + str(n_slow))
    MACDdiff = pd.Series(MACD - MACDsign, name='macddiff_' + str(n_fast) + '_' + str(n_slow))
    df[MACD.name] = MACD
    df[MACDsign.name] = MACDsign
    df[MACDdiff.name] = MACDdiff
    return df


# Mass Index
def MassI(df):
    Range = df['high'] - df['low']
    EX1 = pd.ewma(Range, span=9, min_periods=8)
    EX2 = pd.ewma(EX1, span=9, min_periods=8)
    Mass = EX1 / EX2
    MassI = pd.Series(pd.rolling_sum(Mass, 25), name='mass_index')
    df[MassI.name] = MassI
    return df


# Vortex Indicator: http://www.vortexindicator.com/VFX_VORTEX.PDF
def Vortex(df, n):
    i = 0
    TR = [0]
    while i < df.index[-1]:
        Range = max(df.get_value(i + 1, 'high'), df.get_value(i, 'close')) - min(df.get_value(i + 1, 'low'),
                                                                                 df.get_value(i, 'close'))
        TR.append(Range)
        i = i + 1
    i = 0
    VM = [0]
    while i < df.index[-1]:
        Range = abs(df.get_value(i + 1, 'high') - df.get_value(i, 'low')) - abs(
            df.get_value(i + 1, 'low') - df.get_value(i, 'high'))
        VM.append(Range)
        i = i + 1
    VI = pd.Series(pd.rolling_sum(pd.Series(VM), n) / pd.rolling_sum(pd.Series(TR), n), name='vortex_' + str(n))
    df[VI.name] = VI
    return df


# KST Oscillator
def KST(df, r1, r2, r3, r4, n1, n2, n3, n4):
    M = df['close'].diff(r1 - 1)
    N = df['close'].shift(r1 - 1)
    ROC1 = M / N
    M = df['close'].diff(r2 - 1)
    N = df['close'].shift(r2 - 1)
    ROC2 = M / N
    M = df['close'].diff(r3 - 1)
    N = df['close'].shift(r3 - 1)
    ROC3 = M / N
    M = df['close'].diff(r4 - 1)
    N = df['close'].shift(r4 - 1)
    ROC4 = M / N
    KST = pd.Series(
        pd.rolling_sum(ROC1, n1) + pd.rolling_sum(ROC2, n2) * 2 + pd.rolling_sum(ROC3, n3) * 3 + pd.rolling_sum(ROC4,
                                                                                                                n4) * 4,
        name='kst_' + str(r1) + '_' + str(r2) + '_' + str(r3) + '_' + str(r4) + '_' + str(n1) + '_' + str(
            n2) + '_' + str(n3) + '_' + str(n4))
    df[KST.name] = KST
    return df


# Relative Strength Index
def RSI(df, n):
    i = 0
    UpI = [0]
    DoI = [0]
    while i + 1 <= df.index[-1]:
        UpMove = df.get_value(i + 1, 'high') - df.get_value(i, 'high')
        DoMove = df.get_value(i, 'low') - df.get_value(i + 1, 'low')
        if UpMove > DoMove and UpMove > 0:
            UpD = UpMove
        else:
            UpD = 0
        UpI.append(UpD)
        if DoMove > UpMove and DoMove > 0:
            DoD = DoMove
        else:
            DoD = 0
        DoI.append(DoD)
        i = i + 1
    UpI = pd.Series(UpI)
    DoI = pd.Series(DoI)
    PosDI = pd.Series(pd.ewma(UpI, span=n, min_periods=n - 1))
    NegDI = pd.Series(pd.ewma(DoI, span=n, min_periods=n - 1))
    RSI = pd.Series(PosDI / (PosDI + NegDI), name='rsi_' + str(n))
    df[RSI.name] = RSI
    return df


# True Strength Index
def TSI(df, r, s):
    M = pd.Series(df['close'].diff(1))
    aM = abs(M)
    EMA1 = pd.Series(pd.ewma(M, span=r, min_periods=r - 1))
    aEMA1 = pd.Series(pd.ewma(aM, span=r, min_periods=r - 1))
    EMA2 = pd.Series(pd.ewma(EMA1, span=s, min_periods=s - 1))
    aEMA2 = pd.Series(pd.ewma(aEMA1, span=s, min_periods=s - 1))
    TSI = pd.Series(EMA2 / aEMA2, name='tsi_' + str(r) + '_' + str(s))
    df[TSI.name] = TSI
    return df


# Accumulation/Distribution
def ACCDIST(df, n):
    ad = (2 * df['close'] - df['high'] - df['low']) / (df['high'] - df['low']) * df['volume']
    M = ad.diff(n - 1)
    N = ad.shift(n - 1)
    ROC = M / N
    AD = pd.Series(ROC, name='acc/dist_roc_' + str(n))
    df[AD.name] = AD
    return df


# Chaikin Oscillator
def Chaikin(df):
    ad = (2 * df['close'] - df['high'] - df['low']) / (df['high'] - df['low']) * df['volume']
    Chaikin = pd.Series(pd.ewma(ad, span=3, min_periods=2) - pd.ewma(ad, span=10, min_periods=9), name='chaikin')
    df[Chaikin.name] = Chaikin
    return df


# Money Flow Index and Ratio
def MFI(df, n):
    PP = (df['high'] + df['low'] + df['close']) / 3
    i = 0
    PosMF = [0]
    while i < df.index[-1]:
        if PP[i + 1] > PP[i]:
            PosMF.append(PP[i + 1] * df.get_value(i + 1, 'volume'))
        else:
            PosMF.append(0)
        i = i + 1
    PosMF = pd.Series(PosMF)
    TotMF = PP * df['volume']
    MFR = pd.Series(PosMF / TotMF)
    MFI = pd.Series(pd.rolling_mean(MFR, n), name='mfi_' + str(n))
    df[MFI.name] = MFI
    return df


# On-balance volume
def OBV(df, n):
    i = 0
    OBV = [0]
    while i < df.index[-1]:
        if df.get_value(i + 1, 'close') - df.get_value(i, 'close') > 0:
            OBV.append(df.get_value(i + 1, 'volume'))
        if df.get_value(i + 1, 'close') - df.get_value(i, 'close') == 0:
            OBV.append(0)
        if df.get_value(i + 1, 'close') - df.get_value(i, 'close') < 0:
            OBV.append(-df.get_value(i + 1, 'volume'))
        i = i + 1
    OBV = pd.Series(OBV)
    OBV_ma = pd.Series(pd.rolling_mean(OBV, n), name='obv_' + str(n))
    df[OBV_ma.name] = OBV_ma
    return df


# Force Index
def FORCE(df, n):
    F = pd.Series(df['close'].diff(n) * df['volume'].diff(n), name='force_' + str(n))
    df[F.name] = F
    return df


# Ease of Movement
def EOM(df, n):
    EoM = (df['high'].diff(1) + df['low'].diff(1)) * (df['high'] - df['low']) / (2 * df['volume'])
    Eom_ma = pd.Series(pd.rolling_mean(EoM, n), name='eom_' + str(n))
    df[Eom_ma.name] = Eom_ma
    return df


# Commodity Channel Index
def CCI(df, n):
    PP = (df['high'] + df['low'] + df['close']) / 3
    CCI = pd.Series((PP - pd.rolling_mean(PP, n)) / pd.rolling_std(PP, n), name='cci_' + str(n))
    df[CCI.name] = CCI
    return df


# Coppock Curve
def COPP(df, n):
    M = df['close'].diff(int(n * 11 / 10) - 1)
    N = df['close'].shift(int(n * 11 / 10) - 1)
    ROC1 = M / N
    M = df['close'].diff(int(n * 14 / 10) - 1)
    N = df['close'].shift(int(n * 14 / 10) - 1)
    ROC2 = M / N
    Copp = pd.Series(pd.ewma(ROC1 + ROC2, span=n, min_periods=n), name='copp_' + str(n))
    df[Copp.name] = Copp
    return df


# Keltner Channel
def KELCH(df, n):
    KelChM = pd.Series(pd.rolling_mean((df['high'] + df['low'] + df['close']) / 3, n), name='kelchm_' + str(n))
    KelChU = pd.Series(pd.rolling_mean((4 * df['high'] - 2 * df['low'] + df['close']) / 3, n), name='kelchu_' + str(n))
    KelChD = pd.Series(pd.rolling_mean((-2 * df['high'] + 4 * df['low'] + df['close']) / 3, n), name='kelchd_' + str(n))
    df[KelChM.name] = KelChM
    df[KelChU.name] = KelChU
    df[KelChD.name] = KelChD
    return df


# Ultimate Oscillator
def ULTOSC(df):
    i = 0
    TR_l = [0]
    BP_l = [0]
    while i < df.index[-1]:
        TR = max(df.get_value(i + 1, 'high'), df.get_value(i, 'close')) - min(df.get_value(i + 1, 'low'),
                                                                              df.get_value(i, 'close'))
        TR_l.append(TR)
        BP = df.get_value(i + 1, 'close') - min(df.get_value(i + 1, 'low'), df.get_value(i, 'close'))
        BP_l.append(BP)
        i = i + 1
    UltO = pd.Series((4 * pd.rolling_sum(pd.Series(BP_l), 7) / pd.rolling_sum(pd.Series(TR_l), 7)) + (
                2 * pd.rolling_sum(pd.Series(BP_l), 14) / pd.rolling_sum(pd.Series(TR_l), 14)) + (
                                 pd.rolling_sum(pd.Series(BP_l), 28) / pd.rolling_sum(pd.Series(TR_l), 28)),
                     name='ultimate_osc')
    df[UltO.name] = UltO
    return df


# Donchian Channel
def DONCH(df, n):
    i = 0
    DC_l = []
    while i < n - 1:
        DC_l.append(0)
        i = i + 1
    i = 0
    while i + n - 1 < df.index[-1]:
        DC = max(df['high'].ix[i:i + n - 1]) - min(df['low'].ix[i:i + n - 1])
        DC_l.append(DC)
        i = i + 1
    DonCh = pd.Series(DC_l, name='donchian_' + str(n))
    DonCh = DonCh.shift(n - 1)
    df[DonCh.name] = DonCh
    return df


# Standard Deviation
def STDDEV(df, n):
    stdev = pd.Series(pd.rolling_std(df['close'], n), name='std_' + str(n))
    df[stdev.name] = stdev
    return df
