def V_c_from_dl_fit(dl, dl0, V_c0, A, B, C, D):
    return V_c0 + A / (dl0-dl) + B / (dl0-dl)**2 + C / (dl0-dl)**3 + D / (dl0-dl)**4

