# Eliminar rama ya mergeada

Limpieza post-merge: una rama que ya cumplió su propósito (su PR está
mergeado en `main`) no queda viva. Este command verifica el estado antes
de borrar — nunca borra a ciegas.

## Pasos

1. Identificá la rama a limpiar (la actual si no es `main`, o la que
   indique el usuario).
2. Verificá que el merge haya sido exitoso, no solo intentado. Dos
   chequeos, ambos deben pasar:
   - Si hay PR asociado: `gh pr view <rama> --json state,mergedAt`
     debe mostrar `state: MERGED`. Un merge rechazado (conflictos,
     checks de CI pendientes, falta de permisos) no cumple esto.
   - `git log main..<rama> --oneline` debe salir vacío — confirma que
     los commits realmente llegaron a `main`, no solo que el comando
     de merge se ejecutó.
   Si cualquiera de los dos falla, no borres — avisá y preguntá cómo
   seguir (puede ser un commit huérfano, como el caso resuelto en
   PR #2 de este proyecto).
3. Si hay más de una rama para revisar, chequealas todas antes de
   borrar ninguna (`git branch --format='%(refname:short)'` filtrando
   `main`).
4. Mostrá la lista de ramas confirmadas como mergeadas y esperá
   confirmación antes de borrar.
5. Borrá cada rama confirmada: local (`git branch -D <rama>`) y remota
   (`git push origin --delete <rama>`).
6. Si estabas parado en la rama que se borra, cambiá a `main` primero
   y actualizá (`git pull origin main`).

## Antes de confirmar

- [ ] ¿Cada rama a borrar tiene `git log main..<rama>` vacío?
- [ ] ¿Alguna rama tiene commits sin mergear? Si sí, excluila y avisá.
- [ ] ¿El usuario confirmó la lista final antes de ejecutar el borrado?
