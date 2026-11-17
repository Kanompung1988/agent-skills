# CSI Snapshot Contract Reference

Official docs: https://kubernetes.io/docs/concepts/storage/volume-snapshots/ ; https://kubernetes.io/docs/concepts/storage/volume-snapshot-classes/

Static batch-only review. Class deletionPolicy Delete can remove backing snapshots; multiple default classes for one CSI driver are ambiguous. Pre-provisioned snapshots link VolumeSnapshotContent and VolumeSnapshot by references. Cross-mode restore may need explicit allow-volume-mode-change annotation. Missing references are not evidence of missing cluster resources. Do not claim snapshot readiness, storage driver support, or data recovery.
