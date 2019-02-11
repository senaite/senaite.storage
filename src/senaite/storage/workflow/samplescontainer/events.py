def after_recover_samples(samples_container):
    """Recovers all samples contained in this samples container
    """
    for sample in samples_container.get_samples():
        samples_container.remove_object(sample)
