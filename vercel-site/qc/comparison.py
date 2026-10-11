"""Compare only the declared numeric/string fields, using source tolerances."""
import math

def compare(result,reference):
    if reference is None:
        return {'status':'NO_BOOK_ANSWER','fields':[],
                'note':'The supplied PDF has no printed worked answer for this case.'}
    tolerance=reference['absolute_tolerance']
    if not isinstance(tolerance,(int,float)) or not math.isfinite(tolerance) or tolerance<0:
        raise ValueError('Reference tolerance must be finite and nonnegative')
    rows=[]
    for field,expected in reference['values'].items():
        actual=result.get(field)
        numeric=isinstance(expected,(int,float)) and not isinstance(expected,bool)
        error=abs(actual-expected) if numeric and isinstance(actual,(int,float)) else None
        passed=(error is not None and math.isfinite(actual) and error<=tolerance) if numeric else actual==expected
        rows.append(dict(field=field,expected=expected,actual=actual,absolute_error=error,
                         tolerance=tolerance,passed=passed))
    matched=rows and all(r['passed'] for r in rows)
    status='MATCH' if matched else ('SOURCE_ERRATUM' if reference.get('known_source_error') else 'MISMATCH')
    return dict(status=status,
                provenance=reference['provenance'],fields=rows,note=reference.get('note',''))
