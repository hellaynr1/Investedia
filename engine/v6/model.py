"""JSON-only two-stage logistic inference; facts in, deterministic score out."""
import math


def sigmoid(x):
    return 1/(1+math.exp(-max(-700,min(700,x))))


def encode(features, drop=()):
    # Import the one canonical allowlist. No outcomes, prose, prices or timestamps.
    from tools.v6.evaluate import ALLOWED
    result={}
    for key,f in features.items():
        if key not in ALLOWED:raise ValueError('unapproved model input '+key)
        if key in drop:continue
        value=f['value']
        if value is None:continue
        if isinstance(value,(int,float)) and not isinstance(value,bool):
            if not math.isfinite(value):raise ValueError('non-finite feature')
            result[key]=float(value)
        elif isinstance(value,str):result[key+'='+value]=1.0
        else:raise ValueError('invalid fact type')
    return result


def linear(model, values, names, scales):
    return model['intercept']+sum(w*values.get(n,0)/s for w,n,s in zip(model['coef'],names,scales))


def predict(model, features, material_threshold=None, direction_threshold=None):
    values=encode(features,model.get('drop',[]))
    names,scales=model['feature_names'],model['scales']
    zm=linear(model['material'],values,names,scales)
    zd=linear(model['positive'],values,names,scales)
    pm=sigmoid(model['calibration_material'][0]*zm+model['calibration_material'][1])
    pp=sigmoid(model['calibration_positive'][0]*zd+model['calibration_positive'][1])
    mt=material_threshold if material_threshold is not None else model['thresholds']['material']
    dt=direction_threshold if direction_threshold is not None else model['thresholds']['direction']
    strength=max(pp,1-pp)
    evidence=any(f.get('value') not in (None,'none','not-stated','maintained',0)
                 for k,f in features.items() if k not in model.get('drop',[]))
    direction='none' if not evidence or pm<mt or strength<dt else ('long' if pp>=.5 else 'short')
    return {'direction':direction,'material_score':100*pm,'direction_score':100*strength,
            'confidence':100*pm*strength,'score_is_probability':False}
