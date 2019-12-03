FROM envoyproxy/envoy

ADD ./service-envoy.yaml /etc/service-envoy.yaml
CMD ["envoy", "-c", "/etc/service-envoy.yaml"]