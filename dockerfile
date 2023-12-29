FROM alpine


RUN \
  echo "*** install openvpn server ***" && \
  apk add --no-cache --purge -uU \
    openvpn \
    logrotate && \
  rm -rf /var/cache/apk/* /tmp/* && \
  echo "*** fix logrotate ***" && \
  sed -i "s#/var/log/messages {}.*# #g" /etc/logrotate.conf

VOLUME /etc/openvpn

CMD ["openvpn","--config","/etc/openvpn/client_c1.ovpn"]